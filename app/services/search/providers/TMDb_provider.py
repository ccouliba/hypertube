"""TMDb API - Metadata enrichment for movies and TV shows"""
import re
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from app.core.configs import PROVIDERS_CONFIG as _p

LOGGER: logging.Logger = logging.getLogger(__name__)

_tmdb = _p["tmdb"]

LANGUAGE: str = "en-US"
NAME: str = _tmdb["name"]
MOVIE_URL: str = f"{_tmdb['base_url']}/{_tmdb['search_video']}"
TV_SHOW_URL: str = f"{_tmdb['base_url']}/{_tmdb['search_tv']}"
POSTER_URL: str = f"{_tmdb['image_base_url']}/{_tmdb['poster_size']}"
BACKDROP_URL: str = f"{_tmdb['image_base_url']}/{_tmdb['backdrop_size']}"
DEFAULT_TIMEOUT: int = int(_p["timeout"]["default"])

# Pattern to strip technical tokens from torrent titles
_TITLE_CLEANUP_PATTERN: str = r"(?:\bS\d{1,2}E\d{1,2}\b|\b\d{4}\s+\d{2}\s+\d{2}\b|\b\d{4}\b|\b\d{3,4}p\b|\bHD\b|\bWEB[- ]?DL\b|\bWEB\b|\bBluRay\b|\bDVDRip\b|\bHDRip\b|\bWEBRip\b|\bXviD\b|\bAAC\b|\bH\.?264\b|\bH\.?265\b|\bHEVC\b|\bh264\b|\bh265\b|\bx264\b|\bx265\b|-\w+\b)"


class TMDbProvider:
    """TMDb API provider for metadata enrichment"""
    
    API_KEY: str = _tmdb["api_key"]
    
    @classmethod
    def search_video(
        cls,
        title: str,
        year: Optional[int] = None
    ) -> Optional[dict]:
        """Search movie on TMDb"""
        return cls._query(MOVIE_URL, title, **({"year": year} if year else {}))

    @classmethod
    def search_tv(cls, title: str) -> Optional[dict]:
        """Search TV show on TMDb"""
        return cls._query(TV_SHOW_URL, title)

    @classmethod
    def _query(
        cls,
        url: str,
        title: str,
        **extra_params
    ) -> Optional[dict]:
        """Build params and execute a TMDb search"""
        if not cls.API_KEY:
            return None
        params: dict = {
            "api_key": cls.API_KEY,
            "query": title,
            "language": LANGUAGE,
            **extra_params
        }
        return cls._search(url, params)
    
    @classmethod
    def _search(
        cls,
        url: str,
        params: dict
    ) -> Optional[dict]:
        """Execute TMDb API search"""
        try:
            response: requests.Response = requests.get(
                url,
                params=params,
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            data: dict = response.json()
            if results := data.get("results"):
                return cls._format_metadata(results[0])
            return None
        except requests.RequestException as e:
            LOGGER.error(f"[{NAME}] TMDb request error: {e}")
            return None
    
    @staticmethod
    def _format_metadata(data: dict) -> dict:
        """Format TMDb response"""

        def build_url(
            base: str,
            path: Optional[str]
        ) -> Optional[str]:
            return f"{base}{path}" if path else None
        
        year: Optional[int] = None
        release_date = data.get("release_date") or data.get("first_air_date")
        if release_date:
            try:
                year = int(release_date.split("-")[0])
            except (ValueError, IndexError):
                pass
        return {
            "tmdb_id": data.get("id"),
            "year": year,
            "rating": data.get("vote_average"),
            "vote_count": data.get("vote_count"),
            "popularity": data.get("popularity"),
            "overview": data.get("overview"),
            "poster_path": build_url(
                POSTER_URL,
                data.get("poster_path")
            ),
            "backdrop_path": build_url(
                BACKDROP_URL,
                data.get("backdrop_path")
            ),
        }


def extract_tv_title(torrent_name: str) -> str:
    """Extract clean TV show title from torrent name"""
    title: str = torrent_name.replace(" EZTV", "").strip()
    pattern: str = _TITLE_CLEANUP_PATTERN # Remove quality/format markers and episode info
    if match := re.search(pattern, title, re.IGNORECASE):
        title = title[:match.start()].strip()
    title = title.replace(".", " ").replace("_", " ")
    return re.sub(r'\s+', ' ', title).strip()


def _enrich_one(index_result: tuple[int, dict]) -> tuple[int, dict]:
    """Enrich a single result with TMDb metadata (called in parallel)"""
    i, result = index_result
    # if result.get("thumbnail") and result.get("large_cover"):
    #     return i, result
    def _is_valid_image_url(value: Optional[str]) -> bool:
        return isinstance(value, str) and value.startswith(("http://", "https://"))

    has_valid_thumbnail = _is_valid_image_url(result.get("thumbnail"))
    has_valid_large_cover = _is_valid_image_url(result.get("large_cover"))
    if has_valid_thumbnail and has_valid_large_cover:
        return i, result
    
    provider: Optional[str] = result.get("provider")
    title: Optional[str] = result.get("title")
    if not title:
        result["rating_source"] = provider
        return i, result
    match provider:
        case "YTS":
            tmdb_data: Optional[dict] = TMDbProvider.search_video(
                title,
                result.get("year")
            )
        case "EZTV":
            clean_title: str = extract_tv_title(title)
            tmdb_data: Optional[dict] = TMDbProvider.search_tv(clean_title)
        case _:
            tmdb_data = None

    if tmdb_data:
        result["tmdb_id"] = tmdb_data.get("tmdb_id")
        if tmdb_data.get("year"):
            result["year"] = tmdb_data.get("year")
        result["rating"] = tmdb_data.get("rating")
        result["vote_count"] = tmdb_data.get("vote_count")
        result["popularity"] = tmdb_data.get("popularity")
        if not result.get("synopsis"):
            result["synopsis"] = tmdb_data.get("overview")
        if not result.get("thumbnail"):
            result["thumbnail"] = tmdb_data.get("poster_path")
        if not result.get("large_cover"):
            result["large_cover"] = tmdb_data.get("backdrop_path")
        result["rating_source"] = NAME
    else:
        result["rating_source"] = provider
    return i, result


def enrich_with_tmdb(results: list[dict]) -> list[dict]:
    """Enrich results with TMDb metadata (parallel HTTP calls)"""
    if not results:
        return results
    enriched: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(_enrich_one, (i, result)): i
            for i, result in enumerate(results)
        }
        for future in as_completed(futures):
            i, result = future.result()
            enriched[i] = result
    return [enriched[i] for i in range(len(results))]
