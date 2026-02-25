# """Configuration module - Centralized app configuration

# Provides:
#     - Auth and App-level configuration
#     - Database configuration
#     - Celery/Redis configuration
#     - qBittorrent configuration
#     - Search providers configuration (Torrent)
#     - Environment-specific settings
# """
# from core.configs.general import G_CONFIG as APP_CONFIG
# from core.configs.sqlalchemy import DB_CONFIG
# from core.configs.auth import AUTH_CONFIG
# from core.configs.celery import CELERY_CONFIG
# from core.configs.qbittorrent import QBT_CONFIG
# from core.configs.providers import PROVIDERS_CONFIG

# __all__ = [
#     "APP_CONFIG",
#     "DB_CONFIG",
#     "PROVIDERS_CONFIG",
#     "CELERY_CONFIG",
#     "QBT_CONFIG",
#     "AUTH_CONFIG",
# ]
