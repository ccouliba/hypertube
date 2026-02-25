"""Auth module - Authentication and authorization

Provides:
- User authentication (register, login, token refresh)
- JWT token management
- Auth decorators for protected endpoints
- User models and validators
"""
from app.services.auth.dao import UserDAO
from app.services.auth.models import User
from app.services.auth.service import AuthService
from app.services.auth.validators import UserValidator
from app.services.auth.settings import auth_settings

__all__ = [
    "User",
    "UserDAO",
    "AuthService",
    "UserValidator",
    "auth_settings",
]
