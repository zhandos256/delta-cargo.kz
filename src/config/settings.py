import asyncio
import logging

from aiogram import Bot, Dispatcher

from config.scheduler import scheduler
from config.const import  BOT_TOKEN, LOG_FILE
from handlers.start import router as start_router
from services.parser import main_func


async def on_startup(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    if not scheduler.get_job(job_id="main_func"):
        scheduler.add_job(main_func, 'interval', minutes=15, id="main_func")
    scheduler.start()


async def on_shutdown():
    if scheduler:
        scheduler.shutdown()


async def configure_bot():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    try:
        await dp.start_polling(bot, polling_timeout=5)
    except Exception as e:
        logging.exception(e)
    finally:
        await dp.storage.close()
        await bot.session.close()


def configure_logger():
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    common_params = {
        "level": logging.INFO,
        "format": log_format,
        "datefmt": datefmt,
        "filename": LOG_FILE,
        "filemode": "a"
    }
    logging.basicConfig(**common_params)


def main():
    configure_logger()
    asyncio.run(configure_bot())
