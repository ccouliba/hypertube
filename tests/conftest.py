"""
Global pytest configuration and fixtures
Provides mocks and test data for all test modules
"""
import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


os.environ["FLASK_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["DOWNLOAD_DIR"] = "/tmp/test-downloads"
from pathlib import Path
Path("/tmp/test-downloads").mkdir(parents=True, exist_ok=True)
from app.core.configs import QBT_CONFIG
QBT_CONFIG["downloads"]["directory"] = "/tmp/test-downloads"


@pytest.fixture(scope="session")
def app():
    """Create Flask application for testing"""
    from app.app import create_app
    
    app = create_app(config_name="testing")
    app.config["TESTING"] = True
    
    with app.app_context():
        from app.db.session import db
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Test client for Flask app"""
    return app.test_client()


@pytest.fixture(scope="function")
def app_context(app):
    """Application context for tests"""
    with app.app_context():
        yield
        from app.db.session import db
        db.session.rollback()


@pytest.fixture(scope="function")
def db_session(app_context):
    """Database session for tests"""
    from app.db.session import db
    
    yield db.session
    db.session.expire_all()
    db.session.rollback()


@pytest.fixture
def user_data():
    """Standard user data for testing"""
    return {
        "firstname": "Satoru",
        "lastname": "Gojo",
        "username": "StatoruGojo",
        "email": "satoru@example.com",
        "password": "SecurePass123!",
    }


@pytest.fixture
def test_user(db_session, user_data):
    """Create a test user in the database"""
    import uuid
    from app.services.auth.models import User
    
    unique_suffix = uuid.uuid4().hex[:8]
    user_data_copy = user_data.copy()
    user_data_copy["username"] = f"{user_data['username']}_{unique_suffix}"
    user_data_copy["email"] = f"{unique_suffix}_{user_data['email']}"
    
    user = User(
        firstname=user_data_copy["firstname"],
        lastname=user_data_copy["lastname"],
        username=user_data_copy["username"],
        email=user_data_copy["email"],
    )
    user.set_password(user_data_copy["password"])
    db_session.add(user)
    db_session.commit()
    # Store the actual credentials on the user object for tests
    user._test_password = user_data_copy["password"]
    user._test_data = user_data_copy
    return user


@pytest.fixture
def valid_jwt_token(test_user):
    """Generate a valid JWT token for test user"""
    from app.core.security.jwt_gen import generate_token
    from datetime import timedelta
    import os
    payload = {"user_id": test_user.id, "username": test_user.username}
    expiration = timedelta(hours=24)
    secret = os.getenv("JWT_SECRET_KEY", "test-secret-key")
    return generate_token(payload, expiration, secret)


@pytest.fixture
def auth_headers(valid_jwt_token):
    """Authorization headers with valid token"""
    return {"Authorization": f"Bearer {valid_jwt_token}"}


@pytest.fixture
def invalid_auth_headers():
    """Authorization headers with invalid token"""
    return {"Authorization": "Bearer invalid.token.here"}


@pytest.fixture
def movie_data():
    """Standard movie data for testing"""
    from app.services.video.models import ContentType, DownloadStatus
    return {
        "title": "Interstellar",
        "content_type": ContentType.MOVIE,
        "tmdb_id": "157336",
        "rating": 8.6,
        "year": 2014,
        "synopsis": "A hacker discovers the true nature of reality.",
        "genres": ["Action", "Sci-Fi"],
        "thumbnail": "https://example.com/interstellar.jpg",
        "selected_torrent_hash": "abc123def456",
        "download_status": DownloadStatus.NOT_DOWNLOADED,
        "download_progress": 0,
    }


@pytest.fixture
def tvshow_data():
    """Standard TV show data for testing"""
    from app.services.video.models import ContentType, DownloadStatus
    return {
        "title": "Breaking Bad",
        "content_type": ContentType.TV_SHOW,
        "tmdb_id": "1396",
        "rating": 9.5,
        "year": 2008,
        "synopsis": "A chemistry teacher turns to cooking meth.",
        "genres": ["Drama", "Crime"],
        "thumbnail": "https://example.com/breakingbad.jpg",
        "selected_torrent_hash": "xyz789uvw012",
        "download_status": DownloadStatus.NOT_DOWNLOADED,
        "download_progress": 0,
    }


@pytest.fixture
def search_result_movie():
    """Mock external API response for movie"""
    return {
        "title": "Inception",
        "content_type": "movie",
        "tmdb_id": "27205",
        "rating": 8.8,
        "year": 2010,
        "synopsis": "A thief who steals corporate secrets.",
        "genres": ["Action", "Sci-Fi"],
        "torrents": [
            {
                "hash": "hash1234567890",
                "quality": "1080p",
                "seeds": 150,
                "peers": 50,
                "size": "2.5 GB",
                "url": "magnet:?xt=urn:btih:hash1234567890",
            }
        ],
    }


@pytest.fixture
def search_result_tvshow():
    """Mock external API response for TV show"""
    return {
        "title": "Stranger Things",
        "content_type": "tv_show",
        "tmdb_id": "66732",
        "rating": 8.7,
        "year": 2016,
        "synopsis": "Strange events occur in a small town.",
        "genres": ["Drama", "Fantasy"],
        "seasons": 4,
        "torrents": [
            {
                "hash": "tvhash9876543210",
                "quality": "1080p",
                "seeds": 200,
                "peers": 75,
                "size": "50 GB",
                "url": "magnet:?xt=urn:btih:tvhash9876543210",
            }
        ],
    }


@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis client"""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    monkeypatch.setattr("app.services.search.service._cache", mock_redis)
    return mock_redis


@pytest.fixture
def mock_qbittorrent(monkeypatch):
    """Mock qBittorrent client"""
    mock_qb = MagicMock()
    mock_qb.auth_log_in.return_value = True
    mock_qb.app_version.return_value = "v4.5.0"
    mock_qb.torrents_add.return_value = True
    mock_qb.torrents.return_value = []
    
    monkeypatch.setattr("app.services.torrent.service.Client", lambda **kwargs: mock_qb)
    return mock_qb


@pytest.fixture
def mock_provider_registry(monkeypatch):
    """Mock provider registry for search"""
    mock_registry = MagicMock()
    mock_registry.search.return_value = []
    mock_registry.get_movies_only.return_value = []
    mock_registry.get_tvshows_only.return_value = []
    monkeypatch.setattr(
        "app.services.search.service.Registry",
        mock_registry
    )
    return mock_registry


@pytest.fixture
def auth_service(db_session):
    """AuthService instance for testing"""
    from app.services.auth.service import AuthService
    return AuthService()


@pytest.fixture
def search_service(mock_redis, mock_provider_registry):
    """SearchService instance for testing"""
    from app.services.search.service import SearchService
    service = SearchService()
    service.provider_registry = mock_provider_registry
    return service


@pytest.fixture
def torrent_service(mock_qbittorrent):
    """TorrentService instance for testing"""
    from app.services.torrent.service import TorrentService
    return TorrentService()


@pytest.fixture
def movie_service(db_session):
    """MovieService instance for testing"""
    from app.services.video.movie.service import MovieService
    return MovieService()


@pytest.fixture
def tvshow_service(db_session):
    """TVShowService instance for testing"""
    from app.services.video.tv_show.service import TVShowService
    return TVShowService()


@pytest.fixture
def created_movie(movie_service, movie_data, db_session):
    """Create a movie in DB for testing"""
    video = movie_service.dao.create(**movie_data)
    return video.to_dict()


@pytest.fixture
def created_tvshow(tvshow_service, tvshow_data, db_session):
    """Create a TV show in DB for testing"""
    video = tvshow_service.dao.create(**tvshow_data)
    return video.to_dict()


@pytest.fixture
def error_messages():
    """Common error messages for assertions"""
    from app.core.errors.messages import ERROR_MESSAGES
    return ERROR_MESSAGES


@pytest.fixture
def invalid_login_data():
    """Invalid login credentials"""
    return {
        "username": "nonexistent_user",
        "password": "WrongPassword123!",
    }


@pytest.fixture
def invalid_register_data():
    """Invalid registration data"""
    return {
        "firstname": "",
        "lastname": "",
        "username": "a",  
        "email": "not-an-email",
        "password": "123",  
    }


@pytest.fixture
def test_cases_register():
    """Test cases for registration endpoint"""
    return {
        "valid": {
            "firstname": "Jane",
            "lastname": "Smith",
            "username": "janesmith",
            "email": "jane@example.com",
            "password": "SecurePass456!",
        },
        "duplicate_username": {
            "firstname": "Satoru",
            "lastname": "Gojo",
            "username": "StatoruGojo",  
            "email": "satoru@example.com",
            "password": "SecurePass789!",
        },
        "duplicate_email": {
            "firstname": "Satoru",
            "lastname": "Different",
            "username": "newusername",
            "email": "itachi@example.com",  
            "password": "SecurePass321!",
        },
    }


@pytest.fixture
def pagination_test_cases():
    """Test cases for pagination"""
    return [
        {"page": 1, "limit": 10},
        {"page": 2, "limit": 20},
        {"page": 0, "limit": 10},  
        {"page": 1, "limit": 0},   
        {"page": -1, "limit": -10}, 
    ]


@pytest.fixture(autouse=True)
def cleanup_after_tests(app_context):
    """Cleanup after each test"""
    yield
    from app.db.session import db
    db.session.rollback()

@pytest.fixture(scope="session", autouse=True)
def ensure_test_dirs():
    """Ensure test directories exist"""
    import os
    from pathlib import Path
    
    test_download_dir = os.environ.get("DOWNLOAD_DIR", "/tmp/test-downloads")
    Path(test_download_dir).mkdir(parents=True, exist_ok=True)
    yield
