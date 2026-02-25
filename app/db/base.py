"""Database configuration classes"""
from app.db.settings import db_settings as settings


class Config:
    """Base configuration"""
    SQLALCHEMY_ECHO: bool = settings.get("SQLALCHEMY_ECHO", False)
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = settings.get("SQLALCHEMY_TRACK_MODIFICATIONS", False)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql://{settings.get('DB_DEV_USER', '')}:"
        f"{settings.get('DB_DEV_PASSWORD', '')}@"
        f"{settings.get('DB_DEV_HOST', '')}:"
        f"{settings.get('DB_DEV_PORT', '5432')}/"
        f"{settings.get('DB_DEV_NAME', '')}"
    )


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql://{settings.get('DB_PROD_USER', '')}:"
        f"{settings.get('DB_PROD_PASSWORD', '')}@"
        f"{settings.get('DB_PROD_HOST', '')}:"
        f"{settings.get('DB_PROD_PORT', '5432')}/"
        f"{settings.get('DB_PROD_NAME', '')}"
    )


flask_env: dict[str, type[Config]] = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig,
    "default": DevelopmentConfig
}
