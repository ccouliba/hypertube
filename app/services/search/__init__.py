"""Search domain — multi-provider search, registry and settings"""
from app.services.search.service import SearchService
from app.services.search.registry import provider_registry as Registry
from app.services.search.providers import Provider, TMDbProvider
from app.core.configs import PROVIDERS_CONFIG as _p

providers_settings: dict = {
    "YTS_NAME": _p["yts"]["name"],
    "EZTV_NAME": _p["eztv"]["name"],
    "RESULTS_MAX_PER_PAGE": int(_p["pagination"]["max_per_page"]),
    "RESULTS_TOTAL_RESULTS": int(_p["pagination"]["max_total_results"]),
}

__all__ = [
    "SearchService",
    "Registry",
    "Provider",
    "TMDbProvider",
    "providers_settings",
]
