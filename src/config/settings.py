from pathlib import Path
from datetime import datetime

import pytz
from pydantic import Field
from pydantic_settings import BaseSettings

TIMEZONE = pytz.timezone("Asia/Almaty")

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # /src/config → /src → /
LOGS_DIR = BASE_DIR / "logs"

# Создаём директории при необходимости
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def generate_log_file() -> Path:
    return LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"

class Settings(BaseSettings):
    LOGIN: str
    PASSWORD: str
    LOGIN_URL: str = "https://emir-cargo.kz/login"
    BOT_TOKEN: str
    CHAT_ID: int
    DEBUG: bool

    # Динамическое имя лога по дате
    DB_FILE_PATH: Path = BASE_DIR / "cargo.db"
    SCHEDULER_JOBS_FILE_PATH: Path = BASE_DIR / "jobs.db"
    SCHEDULER_JOBS_DB_URL: str = f'sqlite:///{SCHEDULER_JOBS_FILE_PATH}'
    LOG_FILE: Path = Field(default_factory=generate_log_file)

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()