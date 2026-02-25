"""Providers and torrents settings for
search services"""
providers_settings: dict[str, any] = {}

def _init_settings():
    from app.core.configs.providers import PROVIDERS_CONFIG as p_conf
    providers_settings.update({
        "YTS_NAME": str(p_conf["yts"]["name"]),
        "YTS_CONTENT_TYPE": str(p_conf["yts"]["content"]),
        "YTS_MOVIE_URL": str(f"{p_conf['yts']['base_url']}/{p_conf['yts']['list_movies']}"),
        "YTS_ENABLED": bool(p_conf["yts"]["enabled"]),
        "EZTV_NAME": str(p_conf["eztv"]["name"]),
        "EZTV_CONTENT_TYPE": str(p_conf["eztv"]["content"]),
        "EZTV_TV_SHOW_URL": str(f"{p_conf['eztv']['base_url']}/{p_conf['eztv']['get_torrents']}"),
        "EZTV_ENABLED": bool(p_conf["eztv"]["enabled"]),
        "TMDB_NAME": str(p_conf["tmdb"]["name"]),
        "TMDB_API_KEY": str(p_conf["tmdb"]["api_key"]),
        "TMDB_MOVIE_URL": str(f"{p_conf['tmdb']['base_url']}/{p_conf['tmdb']['search_video']}"),
        "TMDB_TV_SHOW_URL": str(f"{p_conf['tmdb']['base_url']}/{p_conf['tmdb']['search_tv']}"),
        "TMDB_POSTER_SIZE_URL": str(f"{p_conf['tmdb']['image_base_url']}/{p_conf['tmdb']['poster_size']}"),
        "TMDB_BACKDROP_SIZE_URL": str(f"{p_conf['tmdb']['image_base_url']}/{p_conf['tmdb']['backdrop_size']}"),
        "TMDB_ENABLED": bool(p_conf["tmdb"]["enabled"]),
        "TIMEOUT_DEFAULT": int(p_conf["timeout"]["default"]),
        "TIMEOUT_SEARCH": int(p_conf["timeout"]["search"]),
        "RESULTS_MAX_PER_PAGE": int(p_conf["pagination"]["max_per_page"]),
        "RESULTS_MAX_PER_PROVIDER": int(p_conf["pagination"]["max_results_per_provider"]),
        "RESULTS_TOTAL_RESULTS": int(p_conf["pagination"]["max_total_results"]),
        "LANGUAGES_DEFAULT": "en-US",
        "LANGUAGES_SUPPORTED": ["en-US", "fr-FR"],
        "PATTERN": str(r"(?:\bS\d{1,2}E\d{1,2}\b|\b\d{4}\s+\d{2}\s+\d{2}\b|\b\d{4}\b|\b\d{3,4}p\b|\bHD\b|\bWEB[- ]?DL\b|\bWEB\b|\bBluRay\b|\bDVDRip\b|\bHDRip\b|\bWEBRip\b|\bXviD\b|\bAAC\b|\bH\.?264\b|\bH\.?265\b|\bHEVC\b|\bh264\b|\bh265\b|\bx264\b|\bx265\b|-\w+\b)"),
    })

_init_settings()
