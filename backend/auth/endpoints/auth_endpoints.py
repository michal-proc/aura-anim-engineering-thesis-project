import logging

from fastapi import APIRouter, HTTPException, status

from backend.auth.schemas import LoginRequest, TokenResponse
from backend.auth.dependencies import AuthServiceDep
from backend.auth.exceptions import (
    InvalidCredentialsError,
    InactiveUserError,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user with email and password, receive JWT access token"
)
async def login(
    login_data: LoginRequest,
    auth_service: AuthServiceDep
) -> TokenResponse:
    """
    Authenticate user and receive access token.

    The token should be included in subsequent requests as:
    `Authorization: Bearer <token>`

    Args:
        login_data: User credentials
        auth_service: Injected authentication service

    Returns:
        Token response with access token and expiration info

    Raises:
        HTTPException 401: Invalid credentials
        HTTPException 403: Inactive user account
        HTTPException 500: Internal server error
    """

    try:
        token_response = auth_service.authenticate_user(login_data)
        return token_response
    except InvalidCredentialsError as e:
        logger.warning(f"Invalid login attempt for email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except InactiveUserError as e:
        logger.warning(f"Inactive user login attempt: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )
