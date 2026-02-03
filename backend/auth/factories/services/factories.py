from functools import lru_cache

from backend.auth.services import AuthService
from backend.security import PasswordManager
from backend.security import JWTManager


@lru_cache()
def create_auth_service() -> AuthService:
    """Create authentication service instance."""
    password_manager = PasswordManager()
    jwt_manager = JWTManager()
    
    return AuthService(
        password_manager=password_manager,
        jwt_manager=jwt_manager
    )
