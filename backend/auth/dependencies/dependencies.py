"""FastAPI dependencies for authentication."""

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.auth.services.auth_service import AuthService
from backend.auth.factories.services import create_auth_service
from backend.auth.exceptions import UserNotFoundError
from backend.security import (
    ExpiredTokenError,
    InvalidTokenError,
)
from backend.accounts.models import User
from backend.accounts.factories.repositories import create_user_repository


logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_auth_service() -> AuthService:
    """Dependency to inject authentication service."""
    return create_auth_service()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency to get the current authenticated user.

    Validates the JWT token and returns the active user.
    This dependency should be used in endpoints for handling authentication.

    Args:
        credentials: Bearer token from Authorization header
        auth_service: Authentication service

    Returns:
        Authenticated user object

    Raises:
        HTTPException (401): If token is invalid, expired, or user not found
    """
    try:
        token = credentials.credentials
        user_id = auth_service.get_current_user_id(token)

        # Fetch user from database
        with create_user_repository() as user_repo:
            user = user_repo.get_active_user_by_id(user_id)

            if not user:
                logger.warning(f"Token valid but user {user_id} not found or inactive")
                raise UserNotFoundError("User not found or inactive")

            logger.debug(f"User {user.email} authenticated successfully")
            return user

    except (ExpiredTokenError, InvalidTokenError, UserNotFoundError) as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]
