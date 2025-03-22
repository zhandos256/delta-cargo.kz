from datetime import datetime
from pathlib import Path
from datetime import datetime

import pytz

BASE_DIR = Path(__file__).parent.parent

LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOG_FILE = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"

TIMEZONE = pytz.timezone("Asia/Almaty")

BOT_TOKEN = "7460694626:AAGyaxk5l3E8Vf8vcMClHYpL2zW6oqgoR7Q"

DB_FILE_PATH = BASE_DIR / 'cargo.db'
SCHEDULER_JOBS_FILE_PATH = BASE_DIR / "jobs.db"
SCHEDULER_JOBS_DB_URL = f'sqlite:///{SCHEDULER_JOBS_FILE_PATH}'