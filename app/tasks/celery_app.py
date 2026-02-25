from celery import Celery
from celery.schedules import crontab
from app.tasks.settings import CELERY_SETTINGS as settings

celery_app: Celery = Celery(
    "hypertube",
    broker=settings["BROKER_URL"],
    backend=settings["RESULT_BACKEND"]
)

celery_app.conf.update(
    # Serialization
    task_serializer=settings["TASK_SERIALIZER"],
    result_serializer=settings["RESULT_SERIALIZER"],
    accept_content=settings["ACCEPT_CONTENT"],

    # Task execution settings
    task_track_started=settings["TASK_TRACK_STARTED"],
    task_time_limit=settings["TASK_HARD_LIMIT"],
    task_soft_time_limit=settings["TASK_SOFT_LIMIT"],

    # Timezone
    timezone=settings["TIMEZONE"],
    enable_utc=settings["ENABLE_UTC"],

    result_expires=settings["RESULT_EXPIRES"],

    # Worker settings
    worker_prefetch_multiplier=settings["WORKER_MULTIPLIER"],
    worker_max_tasks_per_child=settings["WORKER_MAX_TASKS_PER_CHILD"],
    
    # Logging
    worker_log_level=settings["WORKER_LEVEL"],
    worker_log_format=settings["WORKER_LOG_FORMAT"],
    worker_task_log_format=settings["WORKER_TASK_LOG_FORMAT"],
    worker_redirect_stdouts=settings["WORKER_REDIRECT_STDOUTS"],
    worker_redirect_stdouts_level=settings["WORKER_REDIRECT_STDOUTS_LEVEL"],
    # Broker configuration
    broker_connection_retry_on_startup=settings["CONNECTION_RETRY"],
)

celery_app.conf.beat_schedule = {
    "cleanup-old-videos-daily": {
        "task": "tasks.cleanup_old_videos",
        "schedule": crontab(
            hour=settings["HOUR"],
            minute=settings["MINUTE"]
        ),
        "args": (settings["DAYS"],)
    },
}
