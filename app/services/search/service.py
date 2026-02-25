"""
Search Service - Business logic for movie and TV show search
Provides:
- Unified search across local DB and external providers
- Popular content discovery with DB enrichment
- Result pagination and sorting
"""
from app.services.video.models import Video
from app.services.video.movie.service import MovieService
from app.services.video.tv_show.service import TVShowService
from app.services.search.registry import provider_registry as Registry
from app.services.search.settings import providers_settings

MAX_TOTAL: int = providers_settings["RESULTS_TOTAL_RESULTS"]


class SearchService:
    """Service for video search across local DB and external providers"""
    
    def __init__(self):
        self.movie_service = MovieService()
        self.tvshow_service = TVShowService()
        self.provider_registry = Registry.get_instance()
    
    def _find_video_in_db(
        self,
        external_result: dict
    ) -> Video | None:
        """
        Find a video in DB by torrent hash (primary) or title (fallback)
        Returns the Video object if found, None otherwise
        """
        service = (
            self.movie_service 
            if external_result.get("content_type") == "movie"
            else self.tvshow_service
        )
        if external_result.get("torrents"):
            for torrent in external_result["torrents"]:
                if torrent_hash := torrent.get("hash"):
                    if video := service.get_by_torrent_hash(torrent_hash):
                        return video
        videos = service.dao.get_by_title(external_result["title"])
        return videos[0] if videos else None
        
    def get_popular(
        self,
        page: int = 1,
        limit: int = MAX_TOTAL
    ) -> dict:
        """
        Get popular movies and TV shows separately
        This ensures equal distribution between movies and TV shows
        """
        movies_raw = self.provider_registry.get_movies_only(
            sort_by="rating",
            order="desc",
            limit=limit * 2  # Fetch more to account for pagination
        )
        tvshows_raw = self.provider_registry.get_tvshows_only(
            sort_by="download_count",
            order="desc",
            limit=limit * 2
        )
        for result in movies_raw:
            if video := self._find_video_in_db(result):
                self._enrich_with_db_data(result, video)
            else:
                result.update({
                    "downloaded": False,
                    "download_status": "not_downloaded"
                })
        for result in tvshows_raw:
            if video := self._find_video_in_db(result):
                self._enrich_with_db_data(result, video)
            else:
                result.update({
                    "downloaded": False,
                    "download_status": "not_downloaded"
                })
        movies_raw.sort(
            key=lambda x: (
                not x.get("downloaded", False),
                -(x.get("rating") or 0)
            )
        )
        tvshows_raw.sort(
            key=lambda x: (
                not x.get("downloaded", False),
                -(x.get("download_count") or 0)
            )
        )
        return {
            "movies": self._paginate_results(movies_raw, page, limit),
            "tv_shows": self._paginate_results(tvshows_raw, page, limit),
            "page": page,
            "limit": limit,
            "query": ""
        }
    
    def _enrich_with_db_data(
        self,
        result: dict,
        video: Video
    ) -> dict:
        """Enrich external result with local DB information"""
        result.update({
            "id": video.id,
            "downloaded": True,
            "download_status": video.download_status.value if hasattr(video.download_status, 'value') else str(video.download_status),
            "download_progress": video.download_progress,
            "file_path": video.file_path,
            "provider": "local"
        })
        return result
    
    def _paginate_results(
        self,
        results: list[dict],
        page: int,
        limit: int
    ) -> dict:
        """Helper method to paginate a list of results"""
        total = len(results)
        start = (page - 1) * limit
        end = start + limit
        return {
            "results": results[start:end],
            "total_results": total,
            "total_pages": (total + limit - 1) // limit
        }
    
    def unified_search(
        self,
        query: str,
        page: int,
        limit: int
    ) -> dict:
        """
        Unified search combining local DB and external providers
        If query is empty: returns popular movies
        If query provided: search and sort by title
        Strategy:
        1. Fetch external results (sorted by rating)
        2. Enrich each result with DB data if movie exists locally
        3. Sort: downloaded movies first, then by title (alphabetically)
        4. Paginate
        """
        if not query or query.strip() == "":
            return self.get_popular(page, limit)
        # Cap total results at configured maximum (20)
        fetch_limit = min(MAX_TOTAL, limit * 4)
        external_data = self.provider_registry.search_all(
            query, 
            sort_by="rating", 
            order="desc", 
            page=1, 
            limit=fetch_limit
        )
        results = external_data["results"]
        for result in results:
            if video := self._find_video_in_db(result):
                self._enrich_with_db_data(result, video)
            else:
                result.update({
                    "downloaded": False,
                    "download_status": "not_downloaded"
                })
        results.sort(
            key=lambda x: (
                not x.get("downloaded", False),  # Downloaded first
                x.get("title", "").lower()       # Then alphabetically by title
            )
        )
        movies: list[dict] = [
            r for r in results
                if r.get("content_type") == "movie"
        ]
        tv_shows: list[dict] = [
            r for r in results
                if r.get("content_type") == "tv_show"
        ]
        return {
            "movies": self._paginate_results(movies, page, limit),
            "tv_shows": self._paginate_results(tv_shows, page, limit),
            "page": page,
            "limit": limit,
            "query": query
        }


Search_Service: SearchService = SearchService()
