"""Celery worker."""

from typing import Any

from celery import Celery
from celery.schedules import crontab

from settings import Settings
from spider.project_utilities.save_utilities import remove_old_adv
from spider.scripts import run_crawler

celery = Celery(__name__)
celery.conf.broker_url = Settings.CELERY_BROKER_REDIS_URL
celery.conf.result_backend = Settings.CELERY_RESULT_BACKEND


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs: Any) -> None:  # type: ignore
    """Set periodic tasks."""
    sender.add_periodic_task(
        crontab(hour=Settings.CLEAN_TIME),
        clean_db.s(),
    )
    sender.add_periodic_task(
        crontab(hour=Settings.SCRAP_TIME),
        scrap.s(),
    )


@celery.task(name='scrap')
def scrap() -> None:
    """Run crawler task."""
    run_crawler()


@celery.task(name='clean_db')
def clean_db() -> None:
    """Clean db from old advertisements task."""
    remove_old_adv()
