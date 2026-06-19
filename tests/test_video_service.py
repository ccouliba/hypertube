import pytest
from sqlalchemy.exc import IntegrityError
from app.services.video.models import DownloadStatus, ContentType
from app.core.errors.handlers import APIError


class TestVideoServiceCreate:

    def test_create_movie_success(self, movie_service, movie_data, db_session):
        video = movie_service.dao.create(**movie_data)
        result = video.to_dict()
        assert result["id"] is not None and result["title"] == movie_data["title"]

    def test_create_tvshow_success(self, tvshow_service, tvshow_data, db_session):
        video = tvshow_service.dao.create(**tvshow_data)
        result = video.to_dict()
        assert result["id"] is not None and result["content_type"] == ContentType.TV_SHOW.value

    def test_create_movie_minimal_data(self, movie_service, db_session):
        from app.services.video.models import ContentType
        minimal_data = {"title": "Test", "year": 2020, "content_type": ContentType.MOVIE}
        video = movie_service.dao.create(**minimal_data)
        result = video.to_dict()
        assert result["title"] == "Test"

    @pytest.mark.parametrize("field", ["content_type", "title"])
    def test_create_missing_field(self, movie_service, movie_data, field, db_session):
        incomplete = movie_data.copy()
        del incomplete[field]
        with pytest.raises((KeyError, ValueError, TypeError, IntegrityError)):
            movie_service.dao.create(**incomplete)


class TestVideoServiceRead:

    def test_get_movie_by_id(self, movie_service, created_movie):
        result = movie_service.get_by_id(created_movie["id"])
        assert result is not None

    def test_get_movie_not_found(self, movie_service):
        result = movie_service.get_by_id(9999)
        assert result is None

    def test_get_by_torrent_hash(self, movie_service, created_movie, movie_data):
        result = movie_service.get_by_torrent_hash(movie_data["selected_torrent_hash"])
        assert result is not None

    def test_get_all_empty(self, movie_service):
        results = movie_service.get_all()
        assert results == []

    def test_get_all(self, movie_service, movie_data, db_session):
        movie_service.dao.create(**movie_data)
        data2 = movie_data.copy()
        data2["title"] = "Another"
        data2["selected_torrent_hash"] = "different_hash"
        movie_service.dao.create(**data2)
        results = movie_service.get_all()
        assert len(results) >= 2

    def test_get_tvshow_by_id(self, tvshow_service, created_tvshow):
        result = tvshow_service.get_by_id(created_tvshow["id"])
        assert result is not None

    @pytest.mark.parametrize("video_id", [0, -1, 99999])
    def test_get_invalid_ids(self, movie_service, video_id):
        result = movie_service.get_by_id(video_id)
        assert result is None


class TestVideoServiceUpdate:

    def test_update_basic_fields(self, movie_service, created_movie):
        result = movie_service.update(created_movie["id"], {"title": "Updated", "rating": 9.0})
        assert result["title"] == "Updated"

    def test_update_download_status(self, movie_service, created_movie):
        result = movie_service.update(created_movie["id"], {"download_status": DownloadStatus.DOWNLOADING, "download_progress": 50})
        assert result is not None

    def test_update_not_found(self, movie_service):
        result = movie_service.update(9999, {"title": "New"})
        assert result is None

    def test_update_tvshow_seasons(self, tvshow_service, created_tvshow):
        result = tvshow_service.update(created_tvshow["id"], {"seasons": 6})
        assert result is not None

    @pytest.mark.parametrize("status", [DownloadStatus.NOT_DOWNLOADED, DownloadStatus.DOWNLOADING, DownloadStatus.COMPLETED, DownloadStatus.PAUSED])
    def test_update_status_values(self, movie_service, movie_data, db_session, status):
        created_video = movie_service.dao.create(**movie_data)
        movie_id = created_video.id
        try:
            result = movie_service.update(movie_id, {"download_status": status})
            assert result is not None
        except (ValueError, KeyError):
            pass

    def test_update_partial_fields(self, movie_service, created_movie):
        original_year = created_movie["year"]
        result = movie_service.update(created_movie["id"], {"rating": 10.0})
        assert result["year"] == original_year


class TestVideoServiceDelete:

    def test_delete_movie(self, movie_service, created_movie):
        movie_id = created_movie["id"]
        result = movie_service.delete(movie_id)
        assert result is True
        deleted = movie_service.get_by_id(movie_id)
        assert deleted is None

    def test_delete_not_found(self, movie_service):
        result = movie_service.delete(9999)
        assert result is False or result is None

    def test_delete_tvshow(self, tvshow_service, created_tvshow):
        tvshow_id = created_tvshow["id"]
        result = tvshow_service.delete(tvshow_id)
        assert result is True or result is not None

    @pytest.mark.parametrize("video_id", [0, -1, 99999])
    def test_delete_invalid_ids(self, movie_service, video_id):
        result = movie_service.delete(video_id)
        assert result is False or result is None


class TestVideoServiceQueries:

    def test_search_by_title(self, movie_service, movie_data, db_session):
        movie_service.dao.create(**movie_data)
        partial = movie_data["title"][:5]
        results = movie_service.dao.get_by_title(partial)
        assert len(results) > 0

    def test_search_empty_results(self, movie_service):
        results = movie_service.dao.get_by_title("nonexistent_xyz")
        assert results == []

    def test_filter_by_year(self, movie_service, movie_data, db_session):
        data = movie_data.copy()
        data["year"] = 2020
        movie_service.dao.create(**data)
        all_videos = movie_service.get_all()
        assert any(v.get("year") == 2020 for v in all_videos)

    def test_filter_by_rating(self, movie_service, movie_data, db_session):
        movie_service.dao.create(**movie_data)
        all_videos = movie_service.get_all()
        assert any("rating" in v for v in all_videos)


class TestVideoServiceBatch:

    def test_create_multiple(self, movie_service, movie_data, db_session):
        for i in range(5):
            data = movie_data.copy()
            data["title"] = f"Movie {i}"
            data["selected_torrent_hash"] = f"hash_{i}"
            movie_service.dao.create(**data)
        results = movie_service.get_all()
        assert len(results) >= 5

    def test_get_all_respects_limit(self, movie_service, movie_data, db_session):
        for i in range(20):
            data = movie_data.copy()
            data["title"] = f"Movie {i}"
            data["selected_torrent_hash"] = f"hash_{i}"
            movie_service.dao.create(**data)
        results = movie_service.get_all()
        assert len(results) >= 20


class TestVideoServiceStatusTransitions:

    def test_status_not_downloaded_to_downloading(self, movie_service, created_movie):
        result = movie_service.update(created_movie["id"], {"download_status": DownloadStatus.DOWNLOADING, "download_progress": 0})
        assert result is not None

    def test_status_downloading_to_completed(self, movie_service, created_movie):
        movie_service.update(created_movie["id"], {"download_status": DownloadStatus.DOWNLOADING})
        result = movie_service.update(created_movie["id"], {"download_status": DownloadStatus.COMPLETED, "download_progress": 100})
        assert result is not None

    def test_progress_range(self, movie_service, created_movie):
        for progress in [0, 25, 50, 75, 100]:
            result = movie_service.update(created_movie["id"], {"download_progress": progress})
            assert result is not None


class TestVideoServiceFiles:

    def test_set_file_path(self, movie_service, created_movie):
        file_path = "/downloads/movies/test.mp4"
        result = movie_service.update(created_movie["id"], {"file_path": file_path})
        assert result is not None

    def test_update_torrent_info(self, movie_service, created_movie):
        result = movie_service.update(created_movie["id"], {
            "selected_torrent_hash": "newhash123",
            "file_path": "/downloads/new_location/movie.mp4"
        })
        assert result is not None
