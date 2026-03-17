"""EZTV API provider for TV show torrents search"""
import requests
from app.services.search.providers.base import Provider
from app.core.configs import PROVIDERS_CONFIG as _p

NAME: str = _p["eztv"]["name"]
EZTV_CONTENT: str = _p["eztv"]["content"]
MAX_PER_PAGE: int = _p["pagination"]["max_per_page"]
TIMEOUT: int = int(_p["timeout"]["default"])
GET_TORRENTS_URL: str = f"{_p['eztv']['base_url']}/{_p['eztv']['get_torrents']}"


class EZTVProvider(Provider):
    """EZTV API Provider - TV Shows torrents"""
    
    def search(self, query: str) -> list[dict]:
        """Search TV shows on EZTV by title"""
        torrents: list[dict] = self._fetch_eztv_torrents()
        return self._filter_by_query(torrents, query)
    
    def get_popular(self) -> list[dict]:
        """Get popular TV shows from EZTV (recent torrents)"""
        torrents: list[dict] = self._fetch_eztv_torrents()
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
            data: dict = response.json()
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
        seeds: int = torrent.get("seeds") or 0
        torrents: list[dict] = [{
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

