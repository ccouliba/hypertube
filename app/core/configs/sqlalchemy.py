"""SQLAlchemy configurations"""
import os

DB_CONFIG: dict = {
    "sqlalchemy": {
        "echo": os.getenv("SQLALCHEMY_ECHO", "True").lower() == "true",
        "track_modifications": os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() == "true",
    },
    "dev_env": {
        "user": os.getenv("DB_USER", "hypertube"),
        "password": os.getenv("DB_PASSWORD", "hypertube"),
        "host": os.getenv("DB_HOST", "database"),
        "port": int(os.getenv("DB_PORT") or "5432"),
        "name": os.getenv("DB_NAME", "hypertube"),
    },
    "prod_env": {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT") or "5432"),
        "name": os.getenv("DB_NAME"),
    },
}

# Constructed database URIs
# flask_db_config: dict[str, any] = {
#     "dev": f"postgresql://{db_config['db_dev']['user']}:{db_config['db_dev']['password']}@{db_config['db_dev']['host']}:{db_config['db_dev']['port']}/{db_config['db_dev']['name']}",
#     "prod": f"postgresql://{db_config['db_prod']['user']}:{db_config['db_prod']['password']}@{db_config['db_prod']['host']}:{db_config['db_prod']['port']}/{db_config['db_prod']['name']}",
# }