"""EZTV API provider for TV show torrents search"""
import requests
from app.services.search.providers.base import Provider
from app.services.search.settings import providers_settings as settings

NAME: str = settings["EZTV_NAME"]
EZTV_CONTENT: str = settings["EZTV_CONTENT_TYPE"]
MAX_PER_PAGE: int = int(settings["RESULTS_MAX_PER_PAGE"])
TIMEOUT: int = int(settings["TIMEOUT_DEFAULT"])  
GET_TORRENTS_URL: str = settings["EZTV_TV_SHOW_URL"]


class EZTVProvider(Provider):
    """EZTV API Provider - TV Shows torrents"""
    
    def search(self, query: str) -> list[dict]:
        """Search TV shows on EZTV by title"""
        torrents = self._fetch_eztv_torrents()
        return self._filter_by_query(torrents, query)
    
    def get_popular(self) -> list[dict]:
        """Get popular TV shows from EZTV (recent torrents)"""
        torrents = self._fetch_eztv_torrents()
        return torrents[:MAX_PER_PAGE]
    
    def _fetch_eztv_torrents(self) -> list[dict]:
        """
        Fetch torrents from EZTV API
        Returns:
            List of formatted TV show results
        """
        try:
            response: requests.Response = requests.get(
                GET_TORRENTS_URL,
                params={
                    "limit": MAX_PER_PAGE,
                    "page": 0
                },
                timeout=TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("torrents"):
                return []
            return [self._format_eztv_show(torrent) for torrent in data["torrents"]]
        except requests.RequestException as e:
            return self._handle_request_error(e, NAME)
    
    def _filter_by_query(
            self,
            shows: list[dict],
            query: str
        ) -> list[dict]:
        """Filter shows by query string"""
        query_lower: str = query.lower()
        return [
            show for show in shows 
            if query_lower in show["title"].lower()
        ]
    
    def _format_eztv_show(self, torrent: dict) -> dict:
        """Format EZTV torrent data to standard format"""
        seeds = torrent.get("seeds") or 0
        torrents = [{
            "quality": "TV",
            "type": "tv",
            "size": torrent.get("size_bytes"),
            "url": torrent.get("magnet_url"),
            "hash": torrent.get("hash"),
            "seeds": seeds,
            "peers": torrent.get("peers") or 0
        }]
        return self._format_result(
            data={
                "id": torrent.get("id"),
                "title": torrent.get("title"),
                "year": None,
                "rating": seeds / 10.0 if seeds > 0 else 0,
                "download_count": seeds,
                "synopsis": None,
                "thumbnail": None,
                "large_cover": None,
                "language": "en",
            },
            provider=NAME,
            content_type=EZTV_CONTENT,
            torrents=torrents
        )
    

EZTV_Provider: EZTVProvider = EZTVProvider()
