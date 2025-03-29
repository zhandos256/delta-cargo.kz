from pathlib import Path
from datetime import datetime
from functools import lru_cache
from typing import Optional

import pytz
from pydantic import Field, SecretStr, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Константы конфигурации
TIMEZONE = pytz.timezone("Asia/Almaty")
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
DB_DIR = BASE_DIR / "data"

# Константы для базы данных
MAX_DB_SIZE = 100 * 1024 * 1024  # 100MB
DB_BACKUP_COUNT = 5

# Константы для логов
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Создание необходимых директорий
for directory in [LOGS_DIR, DB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def generate_log_file() -> Path:
    """Генерирует путь к лог-файлу на основе текущей даты."""
    date_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    return LOGS_DIR / f"{date_str}.log"


class Settings(BaseSettings):
    """Конфигурация приложения с загрузкой из .env."""
    
    # Обязательные поля с валидацией
    LOGIN: str = Field(..., min_length=3, max_length=50)
    PASSWORD: SecretStr
    BOT_TOKEN: SecretStr
    CHAT_ID: int = Field(..., gt=0)
    
    # Поля с дефолтными значениями
    LOGIN_URL: HttpUrl = "https://delta-cargo.kz/login"
    DEBUG: bool = False
    
    # Пути к файлам
    DB_FILE_PATH: Path = DB_DIR / "cargo.db"
    SCHEDULER_JOBS_FILE_PATH: Path = DB_DIR / "jobs.db"
    SCHEDULER_JOBS_DB_URL: str = Field(
        default_factory=lambda: f"sqlite:///{DB_DIR / 'jobs.db'}"
    )
    LOG_FILE: Path = Field(default_factory=generate_log_file)
    
    # Настройки базы данных
    DB_MAX_SIZE: int = MAX_DB_SIZE
    DB_BACKUP_COUNT: int = DB_BACKUP_COUNT
    
    # Настройки логов
    LOG_MAX_SIZE: int = MAX_LOG_SIZE
    LOG_BACKUP_COUNT: int = LOG_BACKUP_COUNT
    
    # Настройки приложения
    REQUEST_TIMEOUT: int = 10
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: float = 1.0
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )
    
    @field_validator("DB_FILE_PATH", "SCHEDULER_JOBS_FILE_PATH")
    @classmethod
    def validate_db_paths(cls, v: Path) -> Path:
        """Проверяет и создает директории для файлов базы данных."""
        v.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    @field_validator("LOG_FILE")
    @classmethod
    def validate_log_path(cls, v: Path) -> Path:
        """Проверяет и создает директорию для лог-файла."""
        v.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    @field_validator("LOGIN_URL")
    @classmethod
    def validate_login_url(cls, v: HttpUrl) -> HttpUrl:
        """Проверяет корректность URL для входа."""
        if not str(v).startswith("https://"):
            raise ValueError("LOGIN_URL должен использовать HTTPS")
        return v
    
    class Config:
        """Дополнительные настройки для Pydantic."""
        json_schema_extra = {
            "example": {
                "LOGIN": "user",
                "PASSWORD": "secret",
                "BOT_TOKEN": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                "CHAT_ID": 123456789,
                "DEBUG": False,
            }
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Получает настройки приложения с кэшированием.
    
    Returns:
        Settings: Объект с настройками приложения
    """
    return Settings()


# Инициализация настроек
settings = get_settings()