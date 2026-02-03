"""Account management endpoints."""

import logging
from fastapi import APIRouter, HTTPException, status

from backend.accounts.schemas import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    PasswordChangeRequest,
    AccountDeletionRequest,
    AccountReactivationRequest,
)
from backend.accounts.dependencies import UserServiceDep
from backend.accounts.exceptions import (
    UserAlreadyExistsError,
    InvalidPasswordError,
    UserNotFoundError,
    UserAlreadyActiveError,
)
from backend.accounts.schemas.api_schemas import ForgotPasswordRequest, UserSuccessResponse, PasswordResetRequest
from backend.auth.dependencies import CurrentUser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    response_model=UserSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account"
)
async def register_user(
        user_data: UserCreateRequest,
        user_service: UserServiceDep
) -> UserSuccessResponse:
    """
    Register a new user account.
    
    Args:
        user_data: User registration information
        user_service: Injected user service
        
    Returns:
        Created user information
        
    Raises:
        HTTPException 400: Email or username already exists
        HTTPException 500: Internal server error
    """
    try:
        return user_service.create_user(user_data)
    except UserAlreadyExistsError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )


@router.get(
    "/me",
    response_model=UserSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the authenticated user's profile information"
)
async def get_current_user_profile(
        current_user: CurrentUser
) -> UserSuccessResponse:
    """
    Get current user profile.
    
    Requires authentication.
    
    Args:
        current_user: Automatically injected authenticated user
        
    Returns:
        User profile information
    """
    user_response = UserResponse.model_validate(current_user)
    return UserSuccessResponse(
        success=True,
        data=user_response
    )

@router.put(
    "/me",
    response_model=UserSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Update the authenticated user's profile information"
)
async def update_current_user_profile(
        update_data: UserUpdateRequest,
        current_user: CurrentUser,
        user_service: UserServiceDep
) -> UserSuccessResponse:
    """
    Update current user profile.

    Requires authentication.

    Args:
        update_data: Updated profile information
        current_user: Automatically injected authenticated user
        user_service: Injected user service

    Returns:
        Updated user information

    Raises:
        HTTPException 400: Email or username already taken
        HTTPException 500: Internal server error
    """
    try:
        return user_service.update_user(current_user.id, update_data)
    except UserAlreadyExistsError as e:
        logger.warning(f"Profile update failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Profile update error for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post(
    "/me/change-password",
    response_model=UserSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change the authenticated user's password"
)
async def change_password(
        password_data: PasswordChangeRequest,
        current_user: CurrentUser,
        user_service: UserServiceDep
) -> UserSuccessResponse:
    """
    Change current user password.

    Requires authentication.

    Args:
        password_data: Current and new password
        current_user: Automatically injected authenticated user
        user_service: Injected user service

    Raises:
        HTTPException 400: Current password is incorrect
        HTTPException 500: Internal server error
    """
    try:
        return user_service.change_password(current_user.id, password_data)
    except InvalidPasswordError as e:
        logger.warning(f"Password change failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password change error for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post(
    "/me/deactivate",
    response_model=UserSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate account",
    description="Deactivate the authenticated user's account"
)
async def deactivate_account(
        deletion_request: AccountDeletionRequest,
        current_user: CurrentUser,
        user_service: UserServiceDep
) -> UserSuccessResponse:
    """
    Deactivate current user account.

    The account will be disabled but not permanently deleted.
    User data is retained and the account can potentially be reactivated.

    Deactivated users cannot log in until their account is reactivated.

    Requires authentication and password confirmation.

    Args:
        deletion_request: Password confirmation
        current_user: Automatically injected authenticated user
        user_service: Injected user service

    Raises:
        HTTPException 400: Password incorrect
        HTTPException 500: Internal server error
    """
    try:
        success_response = user_service.deactivate_account(current_user.id, deletion_request.password)
        logger.info(f"User {current_user.id} account deactivated")
        return success_response
    except InvalidPasswordError as e:
        logger.warning(f"Account deactivation failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Account deactivation error for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deactivation failed"
        )

@router.post(
    "/reactivate",
    response_model=UserSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Reactivate account",
    description="Reactivate a deactivated user account"
)
async def reactivate_account(
        reactivation_data: AccountReactivationRequest,
        user_service: UserServiceDep
) -> UserSuccessResponse:
    """
    Reactivate a deactivated account.

    Does not require authentication. Accepts email and password.
    After reactivation, user must log in separately to obtain a JWT token.

    Args:
        reactivation_data: Email and password for verification
        user_service: Injected user service

    Returns:
        Reactivated user information

    Raises:
        HTTPException 400: Account already active
        HTTPException 401: Invalid credentials
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    try:
        return user_service.reactivate_account(
            reactivation_data.email,
            reactivation_data.password
        )
    except UserNotFoundError as e:
        logger.warning(f"Reactivation failed - user not found: {reactivation_data.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidPasswordError as e:
        logger.warning(f"Reactivation failed - invalid password: {reactivation_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except UserAlreadyActiveError as e:
        logger.warning(f"Reactivation failed - account already active: {reactivation_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Account reactivation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account reactivation failed"
        )

@router.delete(
    "/me",
    response_model=UserSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete account",
    description="Permanently delete the authenticated user's account"
)
async def delete_account(
        deletion_request: AccountDeletionRequest,
        current_user: CurrentUser,
        user_service: UserServiceDep
) -> UserSuccessResponse:
    """
    Permanently delete current user account.

    Requires authentication and password confirmation.
    This action is irreversible.

    Args:
        deletion_request: Password confirmation
        current_user: Automatically injected authenticated user
        user_service: Injected user service

    Raises:
        HTTPException 400: Password incorrect
        HTTPException 500: Internal server error
    """
    try:
        success_response = user_service.delete_account(current_user.id, deletion_request.password)
        logger.info(f"User {current_user.id} account deleted")
        return success_response
    except InvalidPasswordError as e:
        logger.warning(f"Account deletion failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Account deletion error for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )

@router.post(
    "/forgot-password",
    response_model=UserSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Simulate sending a password reset email for the given address",
)
async def forgot_password(
        payload: ForgotPasswordRequest,
        user_service: UserServiceDep,
) -> UserSuccessResponse:
    """Simulate forgot password flow.

    Checks if user with given email exists and, if so, acts as if
    a reset email was sent. Always returns success: true, data: null
    for existing users.

    Args:
        payload: Payload with email
        user_service: Injected user service

    Raises:
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    try:
        return user_service.request_password_reset(payload.email)
    except UserNotFoundError as e:
        logger.warning(f"Password reset requested for non-existing user: {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Forgot password error for {payload.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed",
        )

@router.post(
    "/reset-password",
    response_model=UserSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password with token",
    description="Simulate password reset using token, email and new password",
)
async def reset_password(
        payload: PasswordResetRequest,
        user_service: UserServiceDep,
) -> UserSuccessResponse:
    """Reset user password using token + email + new password.

    Token is accepted but not validated (simulation only). If user with
    given email exists, their password is updated.

    Args:
        payload: Token, email and new password
        user_service: Injected user service

    Raises:
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    try:
        return user_service.reset_password_with_token(
            email=payload.email,
            new_password=payload.new_password,
        )
    except UserNotFoundError as e:
        logger.warning(f"Password reset failed - user not found: {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Password reset error for {payload.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed",
        )
