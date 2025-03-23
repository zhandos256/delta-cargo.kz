from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from config.settings import settings, TIMEZONE

jobstores = {
    'default': SQLAlchemyJobStore(url=settings.SCHEDULER_JOBS_DB_URL)
}
job_defaults = {
    'coalesce': True,      # если были пропущенные запуски, выполнить только один
    'max_instances': 1     # не запускать повторно, если ещё выполняется
}
scheduler = BackgroundScheduler(
    jobstores=jobstores, timezone=TIMEZONE,
    job_defaults=job_defaults
)