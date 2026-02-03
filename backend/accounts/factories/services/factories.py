from functools import lru_cache

from backend.accounts.services import UserService
from backend.security import PasswordManager


@lru_cache()
def create_user_service() -> UserService:
    """Create user service instance."""
    password_manager = PasswordManager()
    return UserService(password_manager)
