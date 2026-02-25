# """
# Tasks module - Celery async tasks and torrent management

# This module provides:
#     - Celery settings and task queue
#     - Async download tasks (start, monitor, remove)
#     - Scheduled maintenance tasks (cleanup old videos)
# """
# from app.tasks.celery_app import celery_app
# from app.tasks.settings import CELERY_SETTINGS as celery_settings
# from app.tasks.downloads import (
#     start_torrent_download,
#     monitor_torrent_status,
#     remove_torrent,
#     process_completed_download,
# )
# from app.tasks.maintenance import (
#     cleanup_old_videos,
#     run_daily_maintenance,
# )

# __all__ = [
#     "celery_app",
#     "celery_settings",
#     "start_torrent_download",
#     "monitor_torrent_status",
#     "remove_torrent",
#     "process_completed_download",
#     "cleanup_old_videos",
#     "run_daily_maintenance",
# ]
