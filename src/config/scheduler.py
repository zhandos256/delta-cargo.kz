from typing import Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import settings, TIMEZONE

# Константы для планировщика
DEFAULT_JOB_ID = "main_func"
DEFAULT_INTERVAL_MINUTES = 5
DEFAULT_MISFIRE_GRACE_TIME = 30
DEFAULT_MAX_INSTANCES = 1

def get_jobstores() -> Dict[str, SQLAlchemyJobStore]:
    """Создает и возвращает конфигурацию хранилища задач."""
    return {
        "default": SQLAlchemyJobStore(
            url=settings.SCHEDULER_JOBS_DB_URL,
            tablename="scheduler_jobs",
            engine_options={
                "connect_args": {"check_same_thread": False},
                "pool_pre_ping": True,
            }
        )
    }

def get_job_defaults() -> Dict[str, Any]:
    """Возвращает настройки по умолчанию для задач."""
    return {
        "coalesce": True,
        "max_instances": DEFAULT_MAX_INSTANCES,
        "misfire_grace_time": DEFAULT_MISFIRE_GRACE_TIME,
    }

def get_executors() -> Dict[str, AsyncIOExecutor]:
    """Создает и возвращает конфигурацию исполнителей задач."""
    return {
        "default": AsyncIOExecutor()
    }

def create_scheduler() -> AsyncIOScheduler:
    """Создает и возвращает настроенный планировщик."""
    return AsyncIOScheduler(
        jobstores=get_jobstores(),
        executors=get_executors(),
        job_defaults=get_job_defaults(),
        timezone=TIMEZONE,
    )

# Инициализация планировщика
scheduler = create_scheduler()

def add_default_job(func, **kwargs) -> None:
    """
    Добавляет задачу по умолчанию в планировщик.
    
    Args:
        func: Функция для выполнения
        **kwargs: Дополнительные параметры для задачи
    """
    if not scheduler.get_job(job_id=DEFAULT_JOB_ID, jobstore="default"):
        scheduler.add_job(
            func,
            trigger=IntervalTrigger(minutes=DEFAULT_INTERVAL_MINUTES),
            id=DEFAULT_JOB_ID,
            replace_existing=True,
            **kwargs
        )