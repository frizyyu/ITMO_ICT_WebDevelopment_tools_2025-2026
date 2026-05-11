import os
from datetime import timedelta

from celery import Celery

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery(
    "lr3_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["worker.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    timezone="UTC",
    beat_schedule={
        "parse-default-urls-every-30-minutes": {
            "task": "worker.tasks.parse_default_urls_task",
            "schedule": timedelta(minutes=30),
            "args": (4,),
        },
    },
)
