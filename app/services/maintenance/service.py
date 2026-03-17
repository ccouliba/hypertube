"""MaintenanceService — housekeeping business logic"""
import logging
from app.services.video.movie import MovieDAO
from app.services.video.tv_show import TVShowDAO

LOGGER: logging.Logger = logging.getLogger(__name__)


class MaintenanceService:
    """Logic for maintenance operations (cleanup, housekeeping)"""

    def __init__(self) -> None:
        self.movie_dao: MovieDAO = MovieDAO()
        self.tvshow_dao: TVShowDAO = TVShowDAO()
        LOGGER.info(f"{self.__class__.__name__}: initialized")

    def cleanup_old_videos(self, days: int) -> dict[str, int]:
        """
        Delete movies and TV shows not viewed for more than `days` days.
        Removes both database entries and downloaded files.
        Args:
            days: Retention threshold in days
        Returns:
            Dict with deleted counts per content type and total
        """
        movies_deleted: int = self.movie_dao.cleanup_old_videos(days)
        tvshows_deleted: int = self.tvshow_dao.cleanup_old_videos(days)
        total_deleted: int = movies_deleted + tvshows_deleted
        LOGGER.info(
            f"MaintenanceService: Cleanup completed: {movies_deleted} movies and {tvshows_deleted} "
            f"TV shows deleted (not viewed in {days} days — total: {total_deleted})"
        )
        return {
            "movies_deleted": movies_deleted,
            "tvshows_deleted": tvshows_deleted,
            "total_deleted": total_deleted,
            "days": days,
        }
