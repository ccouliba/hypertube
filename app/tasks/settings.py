"""Celery settings for task queue configuration"""
from app.core.configs import CELERY_CONFIG as config

CELERY_SETTINGS: dict[str, any] = {

    "BROKER_URL": str(config["broker"]["url"]),
    "RESULT_BACKEND": str(config["broker"]["result_backend"]),
    "CONNECTION_RETRY": bool(config["broker"]["connection_retry_on_startup"]),

    "TASK_SERIALIZER": str(config["task"]["serializer"]),
    "ACCEPT_CONTENT": list(config["task"]["accept_content"]),
    "RESULT_SERIALIZER": str(config["task"]["result_serializer"]),
    "TASK_TRACK_STARTED": bool(config["task"]["task_track_started"]),
    "TASK_HARD_LIMIT": int(config["task"]["task_time_limit"]), # 30 minutes,
    "TASK_SOFT_LIMIT": int(config["task"]["task_soft_time_limit"]), # 25 minutes,

    "RETRY_COUNTDOWN": int(config["retry"]["countdown"]),
    "MAX_RETRIES": int(config["retry"]["max_retries"]),

    "DAYS": int(config["maintenance"]["cleanup_days"]),
    "HOUR": int(config["maintenance"]["cleanup_hour"]),
    "MINUTE": int(config["maintenance"]["cleanup_minute"]),

    "TIMEZONE": str(config["timezone"]),
    "ENABLE_UTC": bool(config["enable_utc"]),

    "WORKER_MULTIPLIER": int(config["worker"]["prefech_multiplier"]),
    "WORKER_MAX_TASKS_PER_CHILD": int(config["worker"]["max_tasks_per_child"]),
    "WORKER_LEVEL": str(config["worker"]["log_level"]),
    "WORKER_LOG_FORMAT": str(config["worker"]["log_format"]),
    "WORKER_TASK_LOG_FORMAT": str(config["worker"]["task_log_format"]),
    "WORKER_REDIRECT_STDOUTS": bool(config["worker"]["redirect_stdouts"]),
    "WORKER_REDIRECT_STDOUTS_LEVEL": str(config["worker"]["redirect_stdouts_level"]),

    "RESULT_EXPIRES": int(config["result_backend_expires"]),
}
