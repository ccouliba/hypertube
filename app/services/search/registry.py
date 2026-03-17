"""
External video content providers
Queries multiple sources and aggregates results
Provides:
- Unified search across multiple providers
- Popular content discovery
- Deduplication, sorting, and pagination of results
"""
import logging
from typing import (Callable, Optional)

LOGGER: logging.Logger = logging.getLogger(__name__)
from app.services.search.providers import (
    Provider,
    YTSProvider,
    EZTVProvider,
)
from app.core.configs import PROVIDERS_CONFIG
from app.services.search.providers.TMDb_provider import enrich_with_tmdb
from app.services.search.utils import (
    deduplicate_by_title,
    sort_results,
    paginate
)

MAX_PER_PAGE: int = int(PROVIDERS_CONFIG["pagination"]["max_per_page"])


class ProviderRegistry:
    """
    Manages multiple content providers and aggregates their results
    Orchestrates multiple providers (YTS, EZTV, etc.) to provide unified
    search and popular content with deduplication, sorting, and pagination.
    """
    def __init__(
        self, 
        providers: Optional[list[Provider]] = None
    ) -> None:
        """
        Initialize the provider registry
        Args:
            providers: List of Provider instances (defaults to all available)
        """
        self._providers: list[Provider] = (
            providers 
                if providers is not None 
                    else self._get_default_providers()
        )

    def search_all(
        self,
        query: str,
        sort_by: str = "rating",
        order: str = "desc",
        page: int = 1,
        limit: int = MAX_PER_PAGE
    ) -> dict:
        """
        Search all providers and aggregate results
        Args:
            query: Search term
            sort_by: Field to sort by (rating, year, title)
            order: Sort order (asc, desc)
            page: Page number (starting from 1)
            limit: Number of results per page
        Returns:
            Dictionary with paginated results and metadata
        """
        return self._aggregate_from_providers(
            fetch_provider=(lambda p: p.search(query)),
            sort_by=sort_by,
            order=order,
            page=page,
            limit=limit
        )
    
    def get_popular_all(
        self,
        sort_by: str = "download_count",
        order: str = "desc",
        page: int = 1,
        limit: int = MAX_PER_PAGE
    ) -> dict:
        """
        Get popular content from all providers (no search query)
        Args:
            sort_by: Field to sort by (download_count, seeds, peers, rating, year)
            order: Sort order (asc, desc)
            page: Page number (starting from 1)
            limit: Number of results per page
        Returns:
            Dictionary with paginated results and metadata
        """
        return self._aggregate_from_providers(
            fetch_provider=(lambda p: p.get_popular()),
            sort_by=sort_by,
            order=order,
            page=page,
            limit=limit
        )
    
    def _aggregate_from_providers(
        self,
        fetch_provider: Callable[[Provider], list[dict]],
        sort_by: str,
        order: str,
        page: int,
        limit: int
    ) -> dict:
        """
        Generic aggregation pipeline for provider results
        Args:
            fetch_provider: Function to call on each provider
            sort_by: Field to sort by
            order: Sort order
            page: Page number
            limit: Results per page
        Returns:
            Paginated and processed results
        """
        results: list[dict] = self._collect_from_providers(fetch_provider)
        results = self._process_pipeline(results, sort_by, order)
        return paginate(results, page, limit)
    
    def _collect_from_providers(
        self,
        fetch_provider: Callable[[Provider], list[dict]]
    ) -> list[dict]:
        """
        Collect results from all providers using the given fetch method
        Args:
            fetch_provider: Method to call on each provider
        Returns:
            Aggregated results from all providers
        """
        results: list[dict] = []
        for provider in self._providers:
            try:
                provider_results: list[dict] = fetch_provider(provider)
                results.extend(provider_results)
            except Exception as e:
                provider_name: str = provider.__class__.__name__
                LOGGER.warning(f"ProviderRegistry: error fetching from {provider_name}: {e}")
        return results
    
    def _process_pipeline(
        self,
        results: list[dict],
        sort_by: str,
        order: str
    ) -> list[dict]:
        """
        Process results through enrichment, deduplication, and sorting pipeline
        Args:
            results: Raw results from providers
            sort_by: Sort field
            order: Sort order (asc/desc)
        Returns:
            Processed results
        """
        results: list[dict] = enrich_with_tmdb(results)
        results = deduplicate_by_title(results)
        results = sort_results(results, sort_by, order)
        return results
    
    def _get_default_providers(self) -> list[Provider]:
        """Initialize and return default providers"""
        return [
            YTSProvider(),
            EZTVProvider(),
        ]
    
    def get_movies_only(
        self,
        sort_by: str = "rating",
        order: str = "desc",
        limit: int = MAX_PER_PAGE
    ) -> list[dict]:
        """Get movies from YTS provider only"""
        provider = next((p for p in self._providers if isinstance(p, YTSProvider)), None)
        if provider is None:
            return []
        return self._get_by_content_type(
            provider=provider,
            content_type="movie",
            sort_by=sort_by,
            order=order,
            limit=limit
        )
    
    def get_tvshows_only(
        self,
        sort_by: str = "download_count",
        order: str = "desc",
        limit: int = MAX_PER_PAGE
    ) -> list[dict]:
        """Get TV shows from EZTV provider only"""
        provider = next((p for p in self._providers if isinstance(p, EZTVProvider)), None)
        if provider is None:
            return []
        return self._get_by_content_type(
            provider=provider,
            content_type="tv_show",
            sort_by=sort_by,
            order=order,
            limit=limit
        )
       
    def _get_by_content_type(
        self,
        provider: Provider,
        content_type: str,
        sort_by: str,
        order: str,
        limit: int
    ) -> list[dict]:
        """
        Generic method to fetch content from a specific provider
        Args:
            provider: Provider instance to fetch from
            content_type: Type of content (for error messages)
            sort_by: Field to sort by
            order: Sort order (asc/desc)
            limit: Maximum number of results
        Returns:
            Processed and sorted results
        """
        try:
            results: list[dict] = provider.get_popular()[:limit]
            results = enrich_with_tmdb(results)
            results = sort_results(results, sort_by, order)
            return results
        except Exception as e:
            print(f"Error fetching {content_type}: {e}")
            return []

    def add_provider(self, provider: Provider) -> None:
        """Add a new provider to the registry"""
        if not isinstance(provider, Provider):
            raise TypeError(f"Expected Provider instance, got {type(provider)}")
        self._providers.append(provider)


provider_registry: ProviderRegistry = ProviderRegistry()
