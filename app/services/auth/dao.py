from app.db.session import db
from app.services.auth.models import User

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
        db.session.commit()
        return user
       
    @staticmethod
    def authenticate(username: str, password: str) -> User | None:
        """
        Authenticate a user
        Args:
            username: Username
            password: Plain password
        Returns:
            User if authentication successful, None otherwise
        """
        user: User | None = UserDAO.get_by_username(username)
        if user and user.check_password(password):
            return user
        return None    

    @staticmethod
    def get_all() -> list[User]: # | None:
        """
        Get all users
        Returns:
            list of all users
        """
        return User.query.all()
    
    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        """
        Get a user by ID
        Args:
            user_id: User ID
        Returns:
            User or None if not found
        """
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_username(username: str) -> User | None:
        """
        Get a user by username
        Args:
            username: Username
        Returns:
            User or None if not found
        """
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email: str) -> User | None:
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
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user: User) -> None:
        """
        Delete a user
        Args:
            user: User to delete
        """
        db.session.delete(user)
        db.session.commit()
