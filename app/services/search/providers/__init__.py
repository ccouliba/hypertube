"""Search providers — base class and all provider implementations"""
from app.services.search.providers.base import Provider
from app.services.search.providers.YTS_provider import YTSProvider
from app.services.search.providers.EZTV_provider import EZTVProvider
from app.services.search.providers.TMDb_provider import TMDbProvider

__all__ = [
    "Provider",
    "TMDbProvider",
    "YTSProvider",
    "EZTVProvider",
]
