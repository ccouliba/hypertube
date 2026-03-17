from celery import Celery
from celery.schedules import crontab
from app.core.configs import CELERY_CONFIG

_b: dict[str, str] = CELERY_CONFIG["broker"]
_t: dict[str, str] = CELERY_CONFIG["task"]
_w: dict[str, str] = CELERY_CONFIG["worker"]
_m: dict[str, str] = CELERY_CONFIG["maintenance"]

celery_app: Celery = Celery(
    "hypertube",
    broker=_b["url"],
    backend=_b["result_backend"]
)


# ── Flask app context for tasks that need DB access ──────────────────────────

_flask_app = None

def _get_flask_app():
    """Lazy singleton — creates the Flask app once per worker process."""
    global _flask_app
    if _flask_app is None:
        from app.app import create_app
        _flask_app = create_app()
    return _flask_app


class ContextTask(celery_app.Task):
    """
    Base task class that pushes a Flask application context before running.
    Allows tasks to use Flask-SQLAlchemy, Flask-Migrate, etc.
    """
    abstract: bool = True

    def __call__(self, *args, **kwargs):
        with _get_flask_app().app_context():
            return self.run(*args, **kwargs)


celery_app.Task = ContextTask

# ─────────────────────────────────────────────────────────────────────────────

celery_app.conf.update(
    # Serialization
    task_serializer=_t["serializer"],
    result_serializer=_t["result_serializer"],
    accept_content=_t["accept_content"],

    # Task execution
    task_track_started=_t["task_track_started"],
    task_time_limit=_t["task_time_limit"],
    task_soft_time_limit=_t["task_soft_time_limit"],

    # Timezone
    timezone=CELERY_CONFIG["timezone"],
    enable_utc=CELERY_CONFIG["enable_utc"],

    result_expires=CELERY_CONFIG["result_backend_expires"],

    # Worker
    worker_prefetch_multiplier=_w["prefetch_multiplier"],
    worker_max_tasks_per_child=_w["max_tasks_per_child"],

    # Logging
    worker_log_level=_w["log_level"],
    worker_log_format=_w["log_format"],
    worker_task_log_format=_w["task_log_format"],
    worker_redirect_stdouts=_w["redirect_stdouts"],
    worker_redirect_stdouts_level=_w["redirect_stdouts_level"],

    # Broker
    broker_connection_retry_on_startup=_b["connection_retry_on_startup"],
)

celery_app.conf.beat_schedule = {
    "cleanup-old-videos-daily": {
        "task": "tasks.cleanup_old_videos",
        "schedule": crontab(
            hour=_m["cleanup_hour"],
            minute=_m["cleanup_minute"]
        ),
        "args": (_m["cleanup_days"],)
    },
}
