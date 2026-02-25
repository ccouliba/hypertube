"""DB settings module - Database configuration settings
Provides database settings
"""
from app.core.configs import DB_CONFIG as db_config
from app.core.configs import APP_CONFIG as app_config 


db_settings: dict[str, any] = {
    """Database settings dictionary"""

    "DEBUG": bool(app_config["debug"]),
    "ENV_NAME": str(app_config["app"]["env"]),
    
    "SQLALCHEMY_ECHO": bool(db_config["sqlalchemy"]["echo"]),
    "SQLALCHEMY_TRACK_MODIFICATIONS": bool(db_config["sqlalchemy"]["track_modifications"]),
    "DB_DEV_USER": str(db_config["dev_env"]["user"]),
    "DB_DEV_PASSWORD": str(db_config["dev_env"]["password"]),
    "DB_DEV_HOST": str(db_config["dev_env"]["host"]),
    "DB_DEV_PORT": int(db_config["dev_env"]["port"]),
    "DB_DEV_NAME": str(db_config["dev_env"]["name"]),
    "DB_PROD_USER": str(db_config["prod_env"]["user"]),
    "DB_PROD_PASSWORD": str(db_config["prod_env"]["password"]),
    "DB_PROD_HOST": str(db_config["prod_env"]["host"]),
    "DB_PROD_PORT": int(db_config["prod_env"]["port"]),
    "DB_PROD_NAME": str(db_config["prod_env"]["name"]),
}
