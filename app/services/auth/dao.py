import logging
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import db
from app.services.auth.models import User, RefreshToken
from app.core.errors.handlers import APIError

LOGGER: logging.Logger = logging.getLogger(__name__)

class UserDAO:
    """
    DAO to manage user operations
    """

    @staticmethod
    def create(
        firstname: str,
        lastname: str,
        username: str,
        email: str,
        password: str,
    ) -> User:
        """
        Create a new user        
        Args:
            username: Username
            email: User email
            password: Plain password
        Returns:
            User: Created user
        """
        user: User = User(
            firstname=firstname,
            lastname=lastname,
            username=username,
            email=email
        )
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("UserDAO.create: DB error")
            raise APIError(500, "Database error")
        return user
       
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """
        Authenticate a user
        Args:
            username: Username
            password: Plain password
        Returns:
            User if authentication successful, None otherwise
        """
        user: Optional[User] = UserDAO.get_by_username(username)
        if user and user.check_password(password):
            return user
        return None    

    @staticmethod
    def get_all() -> list[User]:
        """
        Get all users
        Returns:
            list of all users
        """
        return User.query.all()
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """
        Get a user by ID
        Args:
            user_id: User ID
        Returns:
            User or None if not found
        """
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """
        Get a user by username
        Args:
            username: Username
        Returns:
            User or None if not found
        """
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """
        Get a user by email
        Args:
            email: User email
        Returns:
            User or None if not found
        """
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def exists_by_username(username: str) -> bool:
        """
        Check if a user exists by username
        Args:
            username: Username
        Returns:
            True if exists, False otherwise
        """
        return User.query.filter_by(username=username).first() is not None
    
    @staticmethod
    def exists_by_email(email: str) -> bool:
        """
        Check if a user exists by email
        Args:
            email: User email
        Returns:
            True if exists, False otherwise
        """
        return User.query.filter_by(email=email).first() is not None
    
    @staticmethod
    def update(user: User) -> User:
        """
        Update a user
        Args:
            user: User to update
        Returns:
            User: Updated user
        """
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("UserDAO.update: DB error")
            raise APIError(500, "Database error")
        return user
    
    @staticmethod
    def delete(user: User) -> None:
        """
        Delete a user
        Args:
            user: User to delete
        """
        db.session.delete(user)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("UserDAO.delete: DB error")
            raise APIError(500, "Database error")


class RefreshTokenDAO:
    """DAO for refresh token persistence — rotation + revocation"""

    @staticmethod
    def create(user_id: int, expires_days: int) -> tuple[RefreshToken, str]:
        """Persist a new refresh token and return the (model, raw_token) pair"""
        token, raw = RefreshToken.generate(user_id, expires_days)
        db.session.add(token)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("RefreshTokenDAO.create: DB error")
            raise APIError(500, "Database error")
        return token, raw

    @staticmethod
    def get_by_raw(raw_token: str) -> Optional[RefreshToken]:
        """Lookup a token by its raw value (hashed for comparison)"""
        token_hash = RefreshToken.hash_token(raw_token)
        return RefreshToken.query.filter_by(token_hash=token_hash, revoked=False).first()

    @staticmethod
    def revoke(token: RefreshToken) -> None:
        """Mark a single token as revoked"""
        token.revoked = True
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("RefreshTokenDAO.revoke: DB error")
            raise APIError(500, "Database error")

    @staticmethod
    def revoke_all_for_user(user_id: int) -> None:
        """Revoke every active refresh token for a user (e.g. password change, suspicious activity)"""
        RefreshToken.query.filter_by(user_id=user_id, revoked=False).update({"revoked": True})
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("RefreshTokenDAO.revoke_all_for_user: DB error")
            raise APIError(500, "Database error")
