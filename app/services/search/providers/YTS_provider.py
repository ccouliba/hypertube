"""YTS API provider for movie torrents search"""
import requests
from typing import Optional
from app.services.search.providers.base import Provider
from app.services.search.settings import providers_settings as settings

NAME: str = settings["YTS_NAME"]
DEFAULT_TIMEOUT: int = settings["TIMEOUT_DEFAULT"]
RESULTS_PER_PROVIDER: int = settings["RESULTS_MAX_PER_PROVIDER"]
LIST_URLS: str = settings["YTS_MOVIE_URL"]


class YTSProvider(Provider):
    """YTS API Provider - High quality movie torrents"""
    
    def search(self, query: str) -> list[dict]:
        """Search movies on YTS by title"""
        return self._fetch_yts_movies(query_term=query, sort_by="rating")
    
    def get_popular(self) -> list[dict]:
        """Get popular movies from YTS (sorted by downloads)"""
        return self._fetch_yts_movies(sort_by="download_count")
    
    def _fetch_yts_movies(
        self, 
        query_term: Optional[str] = None, 
        sort_by: str = "rating"
    ) -> list[dict]:
        """
        Generic method to fetch movies from YTS API
        Args:
            query_term: Search query (optional)
            sort_by: YTS sort field (rating, download_count, etc.)
        Returns:
            List of formatted movie results
        """
        try:
            params: dict = {
                "limit": RESULTS_PER_PROVIDER,
                "sort_by": sort_by,
                "order_by": "desc"
            }
            if query_term:
                params["query_term"] = query_term
            response: requests.Response = requests.get(
                LIST_URLS,
                params=params,
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "ok" or not data.get("data", {}).get("movies"):
                return []
            return [self._format_yts_movie(movie) for movie in data["data"]["movies"]]
        except requests.RequestException as e:
            return self._handle_request_error(e, NAME)
    
    def _format_yts_movie(self, movie: dict) -> dict:
        """Format YTS movie data to standard format"""
        torrents = [
            {
                "quality": t.get("quality"),
                "type": t.get("type"),
                "size": t.get("size"),
                "url": t.get("url"),
                "hash": t.get("hash"),
                "seeds": t.get("seeds"),
                "peers": t.get("peers")
            }
            for t in movie.get("torrents", [])
        ]
        return self._format_result(
            data={
                "id": movie.get("id"),
                "title": movie.get("title"),
                "year": movie.get("year"),
                "rating": movie.get("rating"),
                "download_count": movie.get("download_count"),
                "genres": movie.get("genres"),
                "synopsis": movie.get("synopsis"),
                "thumbnail": movie.get("medium_cover_image"),
                "large_cover": movie.get("large_cover_image"),
                "language": movie.get("language"),
            },
            provider=NAME is not None,
            content_type="movie",
            torrents=torrents
        )

YTS_Provider: YTSProvider = YTSProvider()
