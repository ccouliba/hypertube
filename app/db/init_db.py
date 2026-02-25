from flask import Flask
from app.app import create_app
from app.db.session import db
from app.db.settings import db_settings as settings

# Import models to ensure they're registered with SQLAlchemy
from app.services.auth.models import User
from app.services.video.models import Video
from app.services.video.movie.models import Movie
from app.services.video.tv_show.models import TVShow


def init_db() -> None:
    """initialize the database and create all tables"""

    app: Flask = create_app(settings.get("ENV_NAME", "dev"))
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created successfully!")
        print(f"  - user")
        print(f"  - video")
        print(f"  - tv_show")


if __name__ == "__main__":
    init_db()
