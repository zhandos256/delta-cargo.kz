import asyncio
import logging

from aiogram import Bot, Dispatcher

from config.logger import setup_logger
from config.settings import settings
from config.scheduler import scheduler, add_default_job
from handlers.start import router as start_router
from services.tracker import main_func

logger = logging.getLogger(__name__)

POLLING_TIMEOUT = 5
SCHEDULER_INTERVAL_MINUTES = 5
SCHEDULER_JOB_ID = "main_func"


async def on_startup(bot: Bot) -> None:
    """Выполняется при запуске бота: удаляет вебхук и настраивает scheduler."""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удалён, пропущены ожидающие обновления.")

        add_default_job(main_func, minutes=SCHEDULER_INTERVAL_MINUTES)
        scheduler.start()
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}", exc_info=True)
        raise


async def on_shutdown(bot: Bot, dp: Dispatcher) -> None:
    """Выполняется при остановке: закрывает scheduler и ресурсы."""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        
        if dp.storage:
            await dp.storage.close()
            logger.info("Хранилище закрыто.")
        
        if bot.session:
            await bot.session.close()
            logger.info("Сессия закрыта.")
    except Exception as e:
        logger.error(f"Ошибка при остановке: {e}", exc_info=True)


async def setup_bot() -> None:
    """Настраивает и запускает бота."""
    bot = Bot(token=settings.BOT_TOKEN)  # Без явной сессии
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot, polling_timeout=POLLING_TIMEOUT)
    except asyncio.CancelledError:
        logger.info("Polling остановлен пользователем.")
    except Exception as e:
        logger.exception(f"Ошибка в polling: {e}")
    finally:
        await on_shutdown(bot, dp)


def main() -> None:
    """Точка входа программы."""
    setup_logger()
    try:
        asyncio.run(setup_bot())
    except KeyboardInterrupt:
        logger.info("Программа остановлена вручную.")
    except Exception as e:
        logger.critical(f"Неустранимая ошибка: {e}", exc_info=True)


if __name__ == "__main__":
    main()