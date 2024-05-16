"""Celery worker."""

from celery import Celery
from celery.schedules import crontab

from settings import Settings
from spider.project_utilities.save_utilities import remove_old_adv
from spider.scripts import run_crawler

celery = Celery(__name__)
celery.conf.broker_url = Settings.CELERY_BROKER_REDIS_URL
celery.conf.result_backend = Settings.CELERY_RESULT_BACKEND


celery.conf.beat_schedule = {
    'clean_db': {
        'task': 'clean_db',
        'schedule': crontab(hour=Settings.CLEAN_TIME, minute='1'),
    },
}
celery.conf.beat_schedule = {
    'scrap': {
        'task': 'scrap',
        'schedule': crontab(hour=Settings.SCRAP_TIME, minute='1'),
    },
}


@celery.task(name='scrap')
def scrap() -> None:
    """Run crawler task."""
    run_crawler()


@celery.task(name='clean_db')
def clean_db() -> None:
    """Clean db from old advertisements task."""
    remove_old_adv()
