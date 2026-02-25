import os

REDIS_BASE_URL: str = os.getenv("REDIS_URL", "redis://redis:6380/")

CELERY_CONFIG: dict = {
    "broker": {
        "url" : os.getenv("CELERY_BROKER_URL", REDIS_BASE_URL+"1"),
        "result_backend" : os.getenv("CELERY_RESULT_BACKEND", REDIS_BASE_URL+"2"),
        "connection_retry_on_startup": True
    },
    "task": {
        "serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "task_track_started": True,
        # 30 * 60 seconds = 30 minutes
        "task_time_limit": int(os.getenv("TASK_TIME_LIMIT", "1800")), 
        # 25 * 60 seconds = 25 minutes
        "task_soft_time_limit": int(os.getenv("TASK_SOFT_TIME_LIMIT", "1500")),
    },
    "retry": {
        "countdown": int(os.getenv("TASK_RETRY_COUNTDOWN", "60")),
        "max_retries": int(os.getenv("TASK_RETRY_MAX", "3")),
    },
    "maintenance": {
        "cleanup_days": int(os.getenv("CLEANUP_OLD_MOVIES_DAYS", "30")),
        "cleanup_hour": int(os.getenv("CLEANUP_HOUR", "11")),
        "cleanup_minute": int(os.getenv("CLEANUP_MINUTE", "0")),
    },
    "timezone": "UTC",
    "enable_utc": True,
    "result_backend_expires": int(os.getenv("CELERY_RESULT_BACKEND_EXPIRES", "3600")),  # 1 hour
    "worker": {
        "prefech_multiplier": int(os.getenv("CELERY_WORKER_PREFETCH_MULTIPLIER", "4")),
        "max_tasks_per_child": int(os.getenv("CELERY_WORKER_MAX_TASKS_PER_CHILD", "1000")),
        "log_level": os.getenv("CELERY_WORKER_LEVEL", "INFO"),
        "log_format": "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        "task_log_format": "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
        "redirect_stdouts": True,
        "redirect_stdouts_level": os.getenv("CELERY_WORKER_LEVEL", "INFO"),
    }
}
