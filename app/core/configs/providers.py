"""Torrent provider configurations"""
import os

PROVIDERS_CONFIG: dict[str, any] = {
    "yts": {
        "name": "YTS",
        "content": "movie",
        "base_url": os.getenv("YTS_BASE_URL", "https://yts.lt/api/v2"),
        "list_movies": "list_movies.json",
        "enabled": os.getenv("YTS_ENABLED", "true").lower() == "true",
    },
    "eztv": {
        "name": "EZTV",
        "content" : "tv_show",
        "base_url": os.getenv("EZTV_BASE_URL", "https://eztvx.to/api"),
        "get_torrents": "get-torrents",
        "enabled": os.getenv("EZTV_ENABLED", "true").lower() == "true",
    },
    "tmdb": {
        "name": "TMDb",
        "base_url": os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3"),
        "api_key": os.getenv("TMDB_API_KEY", ""),
        "image_base_url": os.getenv("TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p"),
        "search_video": "search/movie",
        "search_tv": "search/tv",
        "poster_size": "w500",
        "backdrop_size": "original",
        "enabled": os.getenv("TMDB_ENABLED", "true").lower() == "true",
    },
    "timeout": {
        "default": int(os.getenv("PROVIDER_TIMEOUT", "10")),
        "search": int(os.getenv("SEARCH_TIMEOUT", "15")),
    },
    "pagination": {
        "max_per_page": int(os.getenv("PER_PAGE", "16")),
        "max_results_per_provider": int(os.getenv("MAX_RESULTS_PER_PROVIDER", "20")),
        "max_total_results": int(os.getenv("MAX_TOTAL_RESULTS", "20")),
    }
}
