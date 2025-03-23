import asyncio
import logging

from aiogram import Bot, Dispatcher

from config.logger import setup_logger
from config.settings import settings
from config.scheduler import scheduler
from handlers.start import router as start_router
from services.tracker import main_func

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    if not scheduler.get_job(job_id="main_func"):
        scheduler.add_job(main_func, 'interval', hours=1, id="main_func")
    scheduler.start()


async def on_shutdown():
    if scheduler:
        scheduler.shutdown()


async def setup_bot():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    try:
        await dp.start_polling(bot, polling_timeout=5)
    except Exception as e:
        logger.exception(e)
    finally:
        if dp.storage:
            await dp.storage.close()
        if bot.session:
            await bot.session.close()


if __name__ == "__main__":
    setup_logger()
    asyncio.run(setup_bot())