from typing import Any, Optional
from datetime import timedelta
import logging
from app.core.errors.handlers import APIError
from app.core.errors.messages import ERROR_MESSAGES
from app.core.security.jwt_gen import generate_token
from app.core.configs import AUTH_CONFIG
from app.services.auth.models import RefreshToken, User
from app.services.auth.dao import UserDAO, RefreshTokenDAO

LOGGER: logging.Logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication and user management"""
    
    def __init__(self) -> None:
        self.user_dao: UserDAO = UserDAO()
        self.refresh_token_dao: RefreshTokenDAO = RefreshTokenDAO()
        LOGGER.info(f"{self.__class__.__name__}: initialized")
    
    def register_user(
            self,
            data: dict[str, Any]
        ) -> dict[str, Any]:
        """
        Register a new user
        Args:
            data: Registration data
        Returns:
            Success message with user info
        Raises:
            APIError: If username or email already exists
        """
        if self.user_dao.exists_by_username(data["username"]):
            raise APIError(
                status_code=409, 
                message=ERROR_MESSAGES["USERNAME_EXISTS"]
            )
        if self.user_dao.exists_by_email(data["email"]):
            raise APIError(
                status_code=409,
                message=ERROR_MESSAGES["EMAIL_EXISTS"]
            )
        user: User = self.user_dao.create(**data)
        LOGGER.info(f"AuthService: User registered: username={user.username}")
        return {
            "message": "User registered successfully",
            "user": {
                "username": user.username,
                "profile_picture": user.profile_picture,
            }
        }

    def authenticate_user(
            self,
            data: dict[str, Any]
        ) -> dict[str, Any]:
        """
        Authenticate a user
        Args:
            data: Login credentials
        Returns:
            Success message with user info and JWT token
        Raises:
            APIError: If credentials are invalid
        """
        user: User = self.user_dao.authenticate(
            username=data["username"],
            password=data["password"],
        )
        if not user:
            LOGGER.warning(f"AuthService: Failed login attempt for username='{data.get('username')}'")
            raise APIError(
                status_code=401,
                message=ERROR_MESSAGES["INVALID_CREDENTIALS"]
            )
        LOGGER.info(f"AuthService: User authenticated: username={user.username} id={user.id}")
        access_token: str = self.generate_jwt_token(user)
        _, raw_refresh = self.refresh_token_dao.create(
            user_id=user.id,
            expires_days=AUTH_CONFIG["jwt"]["refresh_token_expires_days"],
        )
        return {
            "message": "Login successful",
            "access_token": access_token,
            "raw_refresh_token": raw_refresh,  # handed to route layer to set cookie
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "profile_picture": user.profile_picture,
            }
        }

    def get_all_users(self) -> list[dict[str, Any]]:
        """Get all users"""
        users: list[User] = self.user_dao.get_all()
        return [
            {
                "id": user.id,
                "username": user.username,
            }
            for user in users
        ]

    def get_user_by_id(
            self, user_id: int,
            base_url: str
        ) -> dict[str, Any]:
        """
        Get a user by ID
        Args:
            user_id: User ID
            base_url: Base URL for profile picture
        Returns:
            User data
        Raises:
            APIError: If user not found
        """
        user: User = self.user_dao.get_by_id(user_id)
        if not user:
            raise APIError(
                status_code=404,
                message=ERROR_MESSAGES["USER_NOT_FOUND"]
            )
        return {
            "username": user.username,
            "email": user.email,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "language": user.language,
            "profile_picture": user.get_profile_picture_url(base_url=base_url),
        }

    def delete_user_by_id(self, user_id: int) -> dict[str, str]:
        """
        Delete a user by ID
        Args:
            user_id: User ID
        Returns:
            Success message
        Raises:
            APIError: If user not found
        """
        user: User = self.user_dao.get_by_id(user_id)
        if not user:
            raise APIError(
                status_code=404,
                message=ERROR_MESSAGES["USER_NOT_FOUND"]
            )
        self.user_dao.delete(user)
        return {"message": "User deleted successfully"}

    def update_user_by_id(
            self,
            user_id: int,
            data: dict[str, Any]
        ) -> dict[str, Any]:
        """
        Update a user's information
        Args:
            user_id: User ID
            data: Update data
        Returns:
            Success message with updated user info
        Raises:
            APIError: If user not found or validation fails
        """
        user: User = self.user_dao.get_by_id(user_id)
        if not user:
            raise APIError(
                status_code=404,
                message=ERROR_MESSAGES["USER_NOT_FOUND"]
            )
        if "username" in data and data["username"] != user.username:
            if self.user_dao.exists_by_username(data["username"]):
                raise APIError(
                    status_code=409,
                    message=ERROR_MESSAGES["USERNAME_EXISTS"]
                )
        if "email" in data and data["email"] != user.email:
            if self.user_dao.exists_by_email(data["email"]):
                raise APIError(
                    status_code=409,
                    message=ERROR_MESSAGES["EMAIL_EXISTS"]
                )
        if "language" in data and data["language"] != user.language:
            if data["language"] not in AUTH_CONFIG["supported_languages"]:
                raise APIError(
                    status_code=400,
                    message=ERROR_MESSAGES["UNSUPPORTED_LANGUAGE"]
                )
        for field, value in data.items():
            setattr(user, field, value)
        self.user_dao.update(user)
        return {
            "message": "User updated successfully",
            "user": {
                "firstname": user.firstname,
                "lastname": user.lastname,
                "username": user.username,
                "email": user.email,
                "language": user.language,
                "profile_picture": user.profile_picture,
            }
        }
    
    def generate_jwt_token(self, user: User) -> str:
        """
        Generate a short-lived JWT access token for an authenticated user
        Args:
            user: Authenticated user
        Returns:
            JWT token string
        """
        secret_key: str = AUTH_CONFIG["jwt"]["secret_key"]
        if not secret_key:
            raise APIError(500, "JWT secret key is not configured")
        payload: dict[str, Any] = {
            "user_id": user.id,
            "username": user.username,
        }
        return generate_token(
            payload=payload,
            expiration=timedelta(minutes=AUTH_CONFIG["jwt"]["access_token_expires_minutes"]),
            secret=secret_key,
            algorithm=AUTH_CONFIG["jwt"]["algorithm"],
        )

    def refresh_access_token(self, raw_token: str) -> dict[str, Any]:
        """
        Validate an existing refresh token, rotate it, and return a new access token.
        Implements refresh token rotation: old token is revoked, new one is issued.
        Args:
            raw_token: Raw refresh token value from httpOnly cookie
        Returns:
            dict with access_token and new raw_refresh_token
        Raises:
            APIError 401 if token is missing, invalid, expired, or revoked
        """
        if not raw_token:
            raise APIError(status_code=401, message=ERROR_MESSAGES["UNAUTHORIZED"])
        token: RefreshToken = self.refresh_token_dao.get_by_raw(raw_token)
        if not token or not token.is_valid():
            LOGGER.warning("AuthService: Refresh token invalid or expired")
            raise APIError(status_code=401, message=ERROR_MESSAGES["UNAUTHORIZED"])
        user: User = self.user_dao.get_by_id(token.user_id)
        if not user:
            LOGGER.warning(f"AuthService: Refresh token references unknown user_id={token.user_id}")
            raise APIError(status_code=401, message=ERROR_MESSAGES["UNAUTHORIZED"])
        self.refresh_token_dao.revoke(token)
        LOGGER.debug(f"AuthService: Refresh token rotated for user_id={user.id}")
        _, new_raw_refresh = self.refresh_token_dao.create(
            user_id=user.id,
            expires_days=AUTH_CONFIG["jwt"]["refresh_token_expires_days"],
        )
        return {
            "access_token": self.generate_jwt_token(user),
            "raw_refresh_token": new_raw_refresh,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "language": user.language,
                "profile_picture": user.profile_picture,
            },
        }

    def logout_user(self, raw_token: str) -> dict[str, str]:
        """
        Revoke the refresh token (server-side logout).
        The client is responsible for clearing the access token from memory.
        Args:
            raw_token: Raw refresh token value from httpOnly cookie
        Returns:
            Success message
        """
        if raw_token:
            token: Optional[RefreshToken] = self.refresh_token_dao.get_by_raw(raw_token)
            if token:
                self.refresh_token_dao.revoke(token)
        return {"message": "Logged out successfully"}
