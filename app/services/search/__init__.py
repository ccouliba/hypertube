"""Search module - Multi-provider video search

Provides:
- Unified search across YTS, EZTV and TMDb
- Popular content discovery
- Provider registry and management
- Search result enrichment with local DB
"""
from app.services.search.settings import providers_settings
from app.services.search.service import SearchService
from app.services.search.registry import provider_registry as Registry
from app.services.search.providers import (
    Provider,
    TMDbProvider,
    YTS_Provider,
    EZTV_Provider,
)

__all__ = [
    "providers_settings",
    "SearchService",
    "Registry",
    "Provider",
    "TMDbProvider",
    "YTS_Provider",
    "EZTV_Provider",
]
