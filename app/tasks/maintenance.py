"""Maintenance tasks for cleaning up old videos"""
import logging
from app.tasks import (
    celery_app,
    celery_settings as settings,
)

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)
CLEANUP_DAYS: int = settings["DAYS"]


@celery_app.task(name="tasks.cleanup_old_videos")
def cleanup_old_videos(days: int = CLEANUP_DAYS) -> dict[str, int]:
    """
    Clean up videos (movies and TV shows) that haven't been viewed for the specified number of days.
    Deletes both database entries and downloaded files.
    This task is scheduled to run daily via Celery Beat.
    Args:
        days: Number of days since last view (default: cf config["maintenance"]["cleanup_days"])
    Returns:
        Dict with deleted counts for movies and TV shows
    """
    from app.services.video.movie import MovieDAO
    from app.services.video.tv_show import TVShowDAO
    try:
        movie_dao = MovieDAO()
        tvshow_dao = TVShowDAO()
        movies_deleted: int = movie_dao.cleanup_old_videos(days)
        tvshows_deleted: int = tvshow_dao.cleanup_old_videos(days)
        total_deleted: int = movies_deleted + tvshows_deleted
        LOGGER.info(
            f"Cleanup task completed: Deleted {movies_deleted} movies and "
            f"{tvshows_deleted} TV shows not viewed in {days} days "
            f"(Total: {total_deleted})"
        )
        return {
            "movies_deleted": movies_deleted,
            "tvshows_deleted": tvshows_deleted,
            "total_deleted": total_deleted,
            "days": days
        }
    except Exception as e:
        LOGGER.error(f"Error during cleanup task: {e}")
        raise


@celery_app.task(name="tasks.run_daily_maintenance")
def run_daily_maintenance() -> dict[str, any]:
    """
    Run all daily maintenance tasks
    """
    LOGGER.info("Starting daily maintenance tasks...")
    result = cleanup_old_videos.delay(CLEANUP_DAYS)
    LOGGER.info("Daily maintenance tasks scheduled")
    return {"status": "scheduled", "task_id": result.id}


if __name__ == "__main__":
    # Can be run manually for testing
    result = cleanup_old_videos(CLEANUP_DAYS)
    print(f"Cleanup result: {result}")
