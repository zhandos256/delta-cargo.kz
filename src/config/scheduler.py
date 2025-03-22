from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from config.const import SCHEDULER_JOBS_DB_URL, TIMEZONE

jobstores = {
    'default': SQLAlchemyJobStore(url=SCHEDULER_JOBS_DB_URL)
}
scheduler = BackgroundScheduler(jobstores=jobstores, timezone=TIMEZONE)