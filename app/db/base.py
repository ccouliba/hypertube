"""Database configuration classes"""
from app.core.configs import DB_CONFIG

def _build_db_uri() -> str:
    db: dict[str, str] = DB_CONFIG["db"]
    return (
        f"postgresql://{db['user']}:"
        f"{db['password']}@"
        f"{db['host']}:"
        f"{db['port']}/"
        f"{db['name']}"
    )


class Config:
    """Base configuration"""
    SQLALCHEMY_ECHO: bool = DB_CONFIG["sqlalchemy"]["echo"]
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = DB_CONFIG["sqlalchemy"]["track_modifications"]
    SQLALCHEMY_DATABASE_URI: str = _build_db_uri()


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG: bool = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG: bool = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG: bool = True
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SQLALCHEMY_ECHO: bool = False


flask_env: dict[str, type[Config]] = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}
