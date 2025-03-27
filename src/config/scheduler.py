from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from config.settings import settings, TIMEZONE

# Конфигурация хранилища задач
jobstores = {
    "default": SQLAlchemyJobStore(
        url=settings.SCHEDULER_JOBS_DB_URL,
        tablename="scheduler_jobs",  # Явное имя таблицы для ясности
    )
}

# Настройки по умолчанию для задач
job_defaults = {
    "coalesce": True,       # Выполнять только один раз при пропущенных запусках
    "max_instances": 1,     # Ограничение на одновременные экземпляры
    "misfire_grace_time": 30,  # Допустимая задержка в секундах перед пропуском
}

# Исполнители задач
executors = {
    "default": AsyncIOExecutor(),
}

# Инициализация планировщика
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=TIMEZONE,
)