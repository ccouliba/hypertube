"""Maintenance tasks — thin Celery wrappers around MaintenanceService"""
import logging
from app.tasks.celery_app import celery_app
from app.core.configs import CELERY_CONFIG as _c
from app.services.maintenance import MaintenanceService

LOGGER = logging.getLogger(__name__)
CLEANUP_DAYS: int = int(_c["maintenance"]["cleanup_days"])


@celery_app.task(name="tasks.cleanup_old_videos")
def cleanup_old_videos(days: int = CLEANUP_DAYS) -> dict[str, int]:
    """
    Clean up videos not viewed for more than `days` days.
    Scheduled daily via Celery Beat.
    """
    LOGGER.info(f"Maintenance: Task cleanup_old_videos started: retention={days} days")
    result: dict[str, int] = MaintenanceService().cleanup_old_videos(days)
    LOGGER.info(f"Maintenance: Task cleanup_old_videos done: {result}")
    return result
