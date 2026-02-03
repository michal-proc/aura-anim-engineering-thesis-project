from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.accounts.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
    
    def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User object if found, None otherwise
        """
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve user by username.
        
        Args:
            username: User's username
            
        Returns:
            User object if found, None otherwise
        """
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_active_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve active user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User object if found and active, None otherwise
        """
        stmt = select(User).where(
            User.id == user_id,
            User.is_active == True
        )
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_active_user_by_email(self, email: str) -> User | None:
        """
        Retrieve active user by email.
        
        Args:
            email: User's email address
            
        Returns:
            User object if found and active, None otherwise
        """
        stmt = select(User).where(
            User.email == email,
            User.is_active == True
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # NOTE:
    # In the mutating methods below the query is flushed to generate
    # the user ID without needing to commit the transaction which should
    # be left to the service layer using this repository.

    def create_user(
        self,
        email: str,
        username: str,
        hashed_password: str,
        full_name: str | None = None
    ) -> User:
        """
        Create a new user.
        
        Args:
            email: User's email address
            username: User's username
            hashed_password: Pre-hashed password
            full_name: User's full name (optional)
            
        Returns:
            Created user object
        """
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True
        )
        self.db.add(user)
        self.db.flush()
        return user
    
    def update_user(
        self,
        user_id: int,
        email: str | None = None,
        username: str | None = None,
        full_name: str | None = None
    ) -> User | None:
        """
        Update user profile information.
        
        Args:
            user_id: User's ID
            email: New email (optional)
            username: New username (optional)
            full_name: New full name (optional)
            
        Returns:
            Updated user object if found, None otherwise
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        if email is not None:
            user.email = email
        if username is not None:
            user.username = username
        if full_name is not None:
            user.full_name = full_name
        
        self.db.flush()
        return user
    
    def update_password(self, user_id: int, hashed_password: str) -> User | None:
        """
        Update user password.
        
        Args:
            user_id: User's ID
            hashed_password: New hashed password
            
        Returns:
            Updated user object if found, None otherwise
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.hashed_password = hashed_password
        self.db.flush()
        return user
    
    def deactivate_user(self, user_id: int) -> User | None:
        """
        Deactivate a user account (soft delete).
        
        Args:
            user_id: User's ID
            
        Returns:
            Deactivated user object if found, None otherwise
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = False
        self.db.flush()
        return user
    
    def reactivate_user(self, user_id: int) -> User | None:
        """
        Reactivate a deactivated user account.

        Args:
            user_id: User's ID
        
        Returns:
            Reactivated user object if found, None otherwise
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = True
        self.db.flush()
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """
        Permanently delete a user account (hard delete).
        
        Args:
            user_id: User's ID
            
        Returns:
            True if user was deleted, False if not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.flush()
        return True
