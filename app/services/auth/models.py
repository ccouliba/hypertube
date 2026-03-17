"""Auth domain models"""
import secrets
import hashlib
from datetime import (datetime, timedelta)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from app.db.session import db
from app.core.configs import APP_CONFIG

BASE_URL: str = APP_CONFIG["app"]["url"]


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


class RefreshToken(db.Model):
    """Opaque refresh token — stored as SHA256 hash, sent as httpOnly cookie"""

    __tablename__ = "refresh_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = db.Column(db.String(64), unique=True, nullable=False)  # SHA256 hex
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(
        "User",
        backref=db.backref("refresh_tokens", lazy="dynamic", cascade="all, delete-orphan"),
    )

    @staticmethod
    def hash_token(raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    @classmethod
    def generate(cls, user_id: int, expires_days: int) -> tuple["RefreshToken", str]:
        """Create a new RefreshToken instance + return the raw token to set in cookie"""
        raw = secrets.token_urlsafe(64)
        instance = cls(
            user_id=user_id,
            token_hash=cls.hash_token(raw),
            expires_at=datetime.utcnow() + timedelta(days=expires_days),
        )
        return instance, raw

    def is_valid(self) -> bool:
        return not self.revoked and self.expires_at > datetime.utcnow()

    def __repr__(self) -> str:
        return f"<RefreshToken user_id={self.user_id} revoked={self.revoked}>"
