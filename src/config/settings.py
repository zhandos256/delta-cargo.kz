from pathlib import Path
from datetime import datetime
from functools import lru_cache

import pytz
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Константы
TIMEZONE = pytz.timezone("Asia/Almaty")
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # /src/config → /src → /
LOGS_DIR = BASE_DIR / "logs"

# Создание директории логов с проверкой
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def generate_log_file() -> Path:
    """Генерирует путь к лог-файлу на основе текущей даты."""
    date_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    return LOGS_DIR / f"{date_str}.log"


class Settings(BaseSettings):
    """Конфигурация приложения с загрузкой из .env."""

    # Обязательные поля
    LOGIN: str
    PASSWORD: str
    BOT_TOKEN: str
    CHAT_ID: int

    # Поля с дефолтными значениями
    LOGIN_URL: str = "https://delta-cargo.kz/login"
    DEBUG: bool = False
    DB_FILE_PATH: Path = BASE_DIR / "cargo.db"
    SCHEDULER_JOBS_FILE_PATH: Path = BASE_DIR / "jobs.db"
    SCHEDULER_JOBS_DB_URL: str = Field(default_factory=lambda: f"sqlite:///{BASE_DIR / 'jobs.db'}")
    LOG_FILE: Path = Field(default_factory=generate_log_file)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Игнорировать лишние переменные в .env
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Инициализация настроек
settings = get_settings()