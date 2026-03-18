from flask import Flask
from app.db.session import db
from app.core.configs import APP_CONFIG

# Import models to ensure they're registered with SQLAlchemy
from app.services.auth.models import (User, RefreshToken)
from app.services.video.models import Video
from app.services.video.movie.models import Movie
from app.services.video.tv_show.models import TVShow


def init_db() -> None:
    """initialize the database and create all tables"""

    from app.app import create_app
    app: Flask = create_app(APP_CONFIG["app"]["env"])
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created successfully!")
        print(f"  - user")
        print(f"  - refresh_token")
        print(f"  - movie")
        print(f"  - tv_show")


if __name__ == "__main__":
    init_db()
