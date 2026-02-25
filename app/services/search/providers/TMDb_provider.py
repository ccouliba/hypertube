"""TMDb API - Metadata enrichment for movies and TV shows"""
import re
import requests
from typing import Optional
from app.services.search import providers_settings as settings

LANGUAGE = settings["LANGUAGES_DEFAULT"]
NAME = settings["TMDB_NAME"]
MOVIE_URL = settings["TMDB_MOVIE_URL"]
TV_SHOW_URL = settings["TMDB_TV_SHOW_URL"]
POSTER_URL = settings["TMDB_POSTER_SIZE_URL"]
BACKDROP_URL = settings["TMDB_BACKDROP_SIZE_URL"]
DEFAULT_TIMEOUT = settings["TIMEOUT_DEFAULT"]


class TMDbProvider:
    """TMDb API provider for metadata enrichment"""
    
    API_KEY: str = settings["TMDB_API_KEY"]
    
    @classmethod
    def search_video(
        cls,
        title: str,
        year: Optional[int] = None
    ) -> Optional[dict]:
        """Search movie on TMDb"""
        if not cls.API_KEY:
            return None
        params: dict = {
            "api_key": cls.API_KEY,
            "query": title,
            "language": LANGUAGE
        }
        if year:
            params["year"] = year
        return cls._search(MOVIE_URL, params)
    
    @classmethod
    def search_tv(cls, title: str) -> Optional[dict]:
        """Search TV show on TMDb"""
        if not cls.API_KEY:
            return None
        params: dict = {
            "api_key": cls.API_KEY,
            "query": title,
            "language": LANGUAGE
        }
        return cls._search(TV_SHOW_URL, params)
    
    @classmethod
    def _search(
        cls,
        url: str,
        params: dict
    ) -> Optional[dict]:
        """Execute TMDb API search"""
        try:
            response = requests.get(
                url,
                params=params,
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            if results := data.get("results"):
                return cls._format_metadata(results[0])
            return None
        except requests.RequestException as e:
            print(f"[{NAME}] error: {e}")
            return None
    
    @staticmethod
    def _format_metadata(data: dict) -> dict:
        """Format TMDb response"""

        def build_url(
            base: str,
            path: Optional[str]
        ) -> Optional[str]:
            return f"{base}{path}" if path else None
        
        year = None
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
    # Remove quality/format markers and episode info
    pattern: str = settings["PATTERN"]
    if match := re.search(pattern, title, re.IGNORECASE):
        title = title[:match.start()].strip()
    title = title.replace(".", " ").replace("_", " ")
    return re.sub(r'\s+', ' ', title).strip()


def enrich_with_tmdb(results: list[dict]) -> list[dict]:
    """Enrich results with TMDb metadata"""
    for i, result in enumerate(results):
        verbose: bool = i < 20  # Log only first 20
        provider: Optional[str] = result.get("provider")
        title: Optional[str] = result.get("title")
        if not title:
            result["rating_source"] = provider
            continue
        match provider:
            case "YTS":
                tmdb_data: Optional[dict] = TMDbProvider.search_video(
                    title,
                    result.get("year")
                )
            case "EZTV":
                clean_title: str = extract_tv_title(title)
                if verbose:
                    print(f"[{NAME}] TV: '{clean_title}'")
                tmdb_data: Optional[dict] = TMDbProvider.search_tv(clean_title)
            case _:
                tmdb_data = None
        
        # Merge metadata if found
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
            if verbose and tmdb_data.get("tmdb_id"):
                print(f"[{NAME}]:: ID: {tmdb_data['tmdb_id']}")
        else:
            result["rating_source"] = provider
    return results
