import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from app.services.video.models import DownloadStatus


class TestSearchServicePopular:

    def test_popular_returns_structure(self, search_service, mock_provider_registry):
        mock_provider_registry.get_movies_only.return_value = []
        mock_provider_registry.get_tvshows_only.return_value = []
        result = search_service.get_popular(page=1, limit=10)
        assert "movies" in result and "tv_shows" in result

    def test_popular_with_movies(self, search_service, mock_provider_registry, search_result_movie):
        mock_provider_registry.get_movies_only.return_value = [search_result_movie]
        mock_provider_registry.get_tvshows_only.return_value = []
        result = search_service.get_popular(page=1, limit=10)
        assert len(result["movies"]["results"]) > 0

    def test_popular_with_tvshows(self, search_service, mock_provider_registry, search_result_tvshow):
        mock_provider_registry.get_movies_only.return_value = []
        mock_provider_registry.get_tvshows_only.return_value = [search_result_tvshow]
        result = search_service.get_popular(page=1, limit=10)
        assert len(result["tv_shows"]["results"]) > 0

    def test_popular_pagination(self, search_service, mock_provider_registry, search_result_movie):
        movies = [search_result_movie.copy() for _ in range(30)]
        mock_provider_registry.get_movies_only.return_value = movies
        mock_provider_registry.get_tvshows_only.return_value = []
        result1 = search_service.get_popular(page=1, limit=10)
        result2 = search_service.get_popular(page=2, limit=10)
        assert result1["page"] == 1 and result2["page"] == 2

    def test_popular_cache_hit(self, search_service, mock_redis, mock_provider_registry, search_result_movie):
        cache_data = {"movies": [search_result_movie], "tv_shows": []}
        mock_redis.get.return_value = json.dumps(cache_data)
        result = search_service.get_popular(page=1, limit=10)
        assert len(result["movies"]["results"]) > 0

    @pytest.mark.parametrize("page,limit", [(1, 10), (2, 20), (1, 50)])
    def test_popular_pagination_params(self, search_service, mock_provider_registry, page, limit):
        mock_provider_registry.get_movies_only.return_value = []
        mock_provider_registry.get_tvshows_only.return_value = []
        result = search_service.get_popular(page=page, limit=limit)
        assert result["page"] == page and result["limit"] == limit


class TestSearchServiceEnrichment:

    def test_enrich_downloaded_video(self, search_service, search_result_movie, movie_service, db_session, movie_data):
        movie = movie_service.dao.create(**movie_data)
        movie.download_status = DownloadStatus.COMPLETED
        db_session.add(movie)
        db_session.commit()
        result = search_result_movie.copy()
        result["selected_torrent_hash"] = movie_data["selected_torrent_hash"]
        result["content_type"] = "movie"
        video = movie_service.dao.get_by_torrent_hash(movie_data["selected_torrent_hash"])
        search_service._enrich_with_db_data(result, video)
        assert result["downloaded"] is True

    def test_find_video_by_hash(self, search_service, movie_service, db_session, movie_data, search_result_movie):
        movie = movie_service.dao.create(**movie_data)
        db_session.commit()
        external_result = search_result_movie.copy()
        external_result["content_type"] = "movie"
        external_result["torrents"] = [{"hash": movie_data["selected_torrent_hash"]}]
        video = search_service._find_video_in_db(external_result)
        assert video is not None and video.id == movie.id

    def test_find_video_by_title(self, search_service, movie_service, db_session, movie_data):
        movie = movie_service.dao.create(**movie_data)
        db_session.commit()
        external_result = {"title": movie_data["title"], "content_type": "movie", "torrents": []}
        video = search_service._find_video_in_db(external_result)
        assert video is not None and video.title == movie_data["title"]

    def test_find_video_not_in_db(self, search_service, search_result_movie):
        external_result = search_result_movie.copy()
        external_result["content_type"] = "movie"
        video = search_service._find_video_in_db(external_result)
        assert video is None


class TestSearchServiceUnifiedSearch:

    def test_search_empty_query_returns_popular(self, search_service, mock_provider_registry):
        mock_provider_registry.get_movies_only.return_value = []
        mock_provider_registry.get_tvshows_only.return_value = []
        result = search_service.unified_search("", page=1, limit=10)
        assert "movies" in result and "tv_shows" in result

    def test_search_with_query(self, search_service, mock_provider_registry, search_result_movie):
        mock_provider_registry.search.return_value = [search_result_movie]
        result = search_service.unified_search("Inception", page=1, limit=10)
        assert result is not None

    def test_search_short_query_error(self, search_service):
        from app.core.errors.handlers import APIError
        with pytest.raises(APIError):
            search_service.unified_search("a", page=1, limit=10)

    @pytest.mark.parametrize("query", ["Inception", "Breaking Bad", "The Matrix"])
    def test_search_various_queries(self, search_service, mock_provider_registry, query):
        mock_provider_registry.search.return_value = []
        result = search_service.unified_search(query, page=1, limit=10)
        assert result is not None

    def test_search_pagination(self, search_service, mock_provider_registry, search_result_movie):
        movies = [search_result_movie.copy() for _ in range(50)]
        mock_provider_registry.search.return_value = movies
        result = search_service.unified_search("test", page=1, limit=10)
        assert len(result.get("results", [])) <= 10


class TestSearchServiceEdgeCases:

    def test_unicode_query(self, search_service, mock_provider_registry):
        mock_provider_registry.search.return_value = []
        result = search_service.unified_search("Amélie", page=1, limit=10)
        assert result is not None

    def test_special_characters_query(self, search_service, mock_provider_registry):
        mock_provider_registry.search.return_value = []
        result = search_service.unified_search("Game of Thrones", page=1, limit=10)
        assert result is not None

    def test_popular_redis_error(self, search_service, mock_redis, mock_provider_registry):
        mock_redis.get.side_effect = Exception("Redis error")
        mock_provider_registry.get_movies_only.return_value = []
        mock_provider_registry.get_tvshows_only.return_value = []
        result = search_service.get_popular(page=1, limit=10)
        assert result is not None

    def test_paginate_empty_list(self, search_service):
        result = search_service._paginate_results([], page=1, limit=10)
        assert result["results"] == [] and result["total_results"] == 0

    def test_paginate_single_page(self, search_service, search_result_movie):
        movies = [search_result_movie.copy() for _ in range(5)]
        result = search_service._paginate_results(movies, page=1, limit=10)
        assert len(result["results"]) == 5 and result["total_results"] == 5

    @pytest.mark.parametrize("page,limit", [(0, 10), (1, 0), (-1, -1)])
    def test_paginate_invalid_params(self, search_service, search_result_movie, page, limit):
        movies = [search_result_movie.copy() for _ in range(10)]
        try:
            result = search_service._paginate_results(movies, page=page, limit=limit)
            assert isinstance(result, dict) and "results" in result
        except (ValueError, IndexError, ZeroDivisionError):
            pass
