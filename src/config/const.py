from datetime import datetime
from pathlib import Path
from datetime import datetime

import pytz

BASE_DIR = Path(__file__).parent.parent

LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOG_FILE = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"

TIMEZONE = pytz.timezone("Asia/Almaty")

BOT_TOKEN = "7460694626:AAGyaxk5l3E8Vf8vcMClHYpL2zW6oqgoR7Q"

DB_FILE_PATH = BASE_DIR / 'data.sqlite'
SCHEDULER_JOBS_FILE_PATH = BASE_DIR / "jobs.sqlite"
SCHEDULER_JOBS_DB_URL = f'sqlite:///{SCHEDULER_JOBS_FILE_PATH}'

from aiogram.types import BotCommand
COMMANDS = [
    BotCommand(command="/start", description="Template start message"),
    BotCommand(command="/help", description="Template help message"),
    BotCommand(command="/menu", description="Template menu message"),
]

CURRENT_DATE = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

HEADLESS = 1

MAIN_URL_LOGIN = 'https://emir-cargo.kz/login/'
LOGIN = '87770153025'
PASSWORD = '123124124g'