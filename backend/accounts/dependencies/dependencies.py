"""FastAPI dependencies for account management."""

from typing import Annotated

from fastapi import Depends

from backend.accounts.services import UserService
from backend.accounts.factories.services import create_user_service


def get_user_service() -> UserService:
    """Dependency to inject user service."""
    return create_user_service()


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
