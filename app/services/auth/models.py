"""Auth domain models"""
from datetime import datetime
from werkzeug.security import (
    generate_password_hash, 
    check_password_hash
)
from app.db.session import db
from app.services.auth.settings import auth_settings as settings

BASE_URL: str = settings.get("APP_URL", "http://localhost:5000")


class User(db.Model):
    """User model representing application users"""

    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    lastname = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(10), default="en")
    profile_picture = db.Column(db.String(255), default="default.png")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password) -> None:
        """Hash and store the password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password) -> bool:
        """Check if the password is correct"""
        return check_password_hash(self.password, password)
    
    def get_profile_picture_url(
        self,
        base_url: str=BASE_URL
    ) -> str:
        """Get the full URL for the profile picture"""
        if self.profile_picture.startswith(('http://', 'https://')):
            return self.profile_picture
        return f"{base_url}/static/profile_pictures/{self.profile_picture}"
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"
