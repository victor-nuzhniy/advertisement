"""Celery worker."""

from celery import Celery

from settings import Settings

celery = Celery(__name__)
celery.conf.broker_url = Settings.CELERY_BROKER_REDIS_URL
celery.conf.result_backend = Settings.CELERY_RESULT_BACKEND
