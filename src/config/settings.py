import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from config.const import  BOT_TOKEN, COMMANDS, TIMEZONE, SCHEDULER_JOBS_DB_URL, LOG_FILE
from handlers.start import router as start_router
from services.parser.main import run_parser

jobstores = {
    'default': SQLAlchemyJobStore(url=SCHEDULER_JOBS_DB_URL)
}
scheduler = BackgroundScheduler()
scheduler.configure(jobstores=jobstores, timezone=TIMEZONE)


async def on_startup(bot: Bot):
    await bot.set_my_commands(commands=COMMANDS)
    await bot.delete_webhook(drop_pending_updates=True)

    scheduler.add_job(run_parser, 'cron', hour="9,12,15,18", minute=0)
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
