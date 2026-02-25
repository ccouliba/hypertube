"""Search providers package initialization

Provides:
- Base Provider class
- YTS Provider and a singleton instance
- EZTV Provider and a singleton instance
- TMDb Provider and a singleton instance
"""
from app.services.search.providers.base import Provider
from app.services.search.providers.YTS_provider import YTS_Provider
from app.services.search.providers.EZTV_provider import EZTV_Provider
from app.services.search.providers.TMDb_provider import TMDbProvider

__all__ = [
    "Provider",
    "TMDbProvider",
    "YTS_Provider",
    "EZTV_Provider",
]
