import logging

from backend.accounts.schemas import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    PasswordChangeRequest,
)
from backend.accounts.factories.repositories import create_user_repository
from backend.accounts.schemas.api_schemas import UserSuccessResponse
from backend.security.password_manager import PasswordManager
from backend.accounts.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidPasswordError,
    UserAlreadyActiveError,
)

logger = logging.getLogger(__name__)


class UserService:
    """Handles user account operations."""

    def __init__(self, password_manager: PasswordManager):
        """
        Args:
            password_manager: Password hashing/verification utility
        """
        self.password_manager = password_manager

    def create_user(self, user_data: UserCreateRequest) -> UserSuccessResponse:
        """
        Create a new user account.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user information
            
        Raises:
            UserAlreadyExistsError: If email or username already exists
        """
        try:
            with create_user_repository() as user_repo:
                if user_repo.get_user_by_email(user_data.email):
                    raise UserAlreadyExistsError("Email already registered")

                if user_repo.get_user_by_username(user_data.username):
                    raise UserAlreadyExistsError("Username already taken")

                hashed_password = self.password_manager.hash_password(
                    user_data.password
                )

                user = user_repo.create_user(
                    email=user_data.email,
                    username=user_data.username,
                    hashed_password=hashed_password,
                    full_name=user_data.full_name,
                )

                logger.info(f"User created: {user.email} (ID: {user.id})")

                user_response = UserResponse.model_validate(user)
                return UserSuccessResponse(
                    success=True,
                    data=user_response
                )

        except UserAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Failed to create user: {e}", exc_info=True)
            raise RuntimeError(f"User creation failed: {e}")

    def get_user(self, user_id: int) -> UserSuccessResponse:
        """
        Get user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User information
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        try:
            with create_user_repository() as user_repo:
                user = user_repo.get_user_by_id(user_id)

                if not user:
                    raise UserNotFoundError(f"User {user_id} not found")

                user_response = UserResponse.model_validate(user)
                return UserSuccessResponse(
                    success=True,
                    data=user_response
                )

        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to retrieve user: {e}")

    def update_user(
            self,
            user_id: int,
            update_data: UserUpdateRequest
    ) -> UserSuccessResponse:
        """
        Update user profile information.
        
        Args:
            user_id: User's ID
            update_data: Updated profile information
            
        Returns:
            Updated user information
            
        Raises:
            UserNotFoundError: If user doesn't exist
            UserAlreadyExistsError: If new email/username already taken
        """
        try:
            with create_user_repository() as user_repo:
                user = user_repo.get_user_by_id(user_id)
                if not user:
                    raise UserNotFoundError(f"User {user_id} not found")

                # Check if new email is already taken
                if update_data.email and update_data.email != user.email:
                    existing_user = user_repo.get_user_by_email(update_data.email)
                    if existing_user and existing_user.id != user_id:
                        raise UserAlreadyExistsError("Email already registered")

                # Check if new username is already taken
                if update_data.username and update_data.username != user.username:
                    existing_user = user_repo.get_user_by_username(update_data.username)
                    if existing_user and existing_user.id != user_id:
                        raise UserAlreadyExistsError("Username already taken")

                updated_user = user_repo.update_user(
                    user_id=user_id,
                    email=update_data.email,
                    username=update_data.username,
                    full_name=update_data.full_name,
                )

                logger.info(f"User {user_id} profile updated")

                user_response = UserResponse.model_validate(updated_user)
                return UserSuccessResponse(
                    success=True,
                    data=user_response
                )

        except (UserNotFoundError, UserAlreadyExistsError):
            raise
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}", exc_info=True)
            raise RuntimeError(f"User update failed: {e}")

    def change_password(
            self,
            user_id: int,
            password_data: PasswordChangeRequest
    ) -> UserSuccessResponse:
        """
        Change user password.
        
        Args:
            user_id: User's ID
            password_data: Current and new password
            
        Raises:
            UserNotFoundError: If user doesn't exist
            InvalidPasswordError: If current password is incorrect
        """
        try:
            with create_user_repository() as user_repo:
                user = user_repo.get_user_by_id(user_id)
                if not user:
                    raise UserNotFoundError(f"User {user_id} not found")

                if not self.password_manager.verify_password(
                        password_data.current_password,
                        user.hashed_password
                ):
                    raise InvalidPasswordError("Current password is incorrect")

                new_hashed_password = self.password_manager.hash_password(
                    password_data.new_password
                )

                user_repo.update_password(user_id, new_hashed_password)

                logger.info(f"Password changed for user {user_id}")

                return UserSuccessResponse(
                    success=True,
                    data=None
                )

        except (UserNotFoundError, InvalidPasswordError):
            raise
        except Exception as e:
            logger.error(f"Failed to change password for user {user_id}: {e}", exc_info=True)
            raise RuntimeError(f"Password change failed: {e}")

    def request_password_reset(self, email: str) -> UserSuccessResponse:
        """Simulate password reset request (forgot password).

        Checks if user with given email exists and logs the request.
        No email is actually sent.

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        try:
            with create_user_repository() as user_repo:
                user = user_repo.get_user_by_email(email)
                if not user:
                    raise UserNotFoundError("User not found")

                # TODO: handle sending e-mail, this endpoint is only for testing

                logger.info(f"Password reset requested for {email}")

                return UserSuccessResponse(
                    success=True,
                    data=None
                )
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to request password reset for {email}: {e}", exc_info=True)
            raise RuntimeError(f"Password reset request failed: {e}")

    def reset_password_with_token(self, email: str, new_password: str) -> UserSuccessResponse:
        """Reset password using a token, email and new password.

        Token is accepted but not validated (simulation).

        Args:
            email: User email
            new_password: New password in plain text

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        try:
            with create_user_repository() as user_repo:
                user = user_repo.get_user_by_email(email)
                if not user:
                    raise UserNotFoundError("User not found")

                # TODO: handle token verification

                new_hashed_password = self.password_manager.hash_password(new_password)
                user_repo.update_password(user.id, new_hashed_password)
                logger.info(f"Password reset via token for user {user.id}")

                user_response = UserResponse.model_validate(user)
                return UserSuccessResponse(
                    success=True,
                    data=user_response
                )
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to reset password for {email}: {e}", exc_info=True)
            raise RuntimeError(f"Password reset failed: {e}")

    def deactivate_account(self, user_id: int, password: str) -> UserSuccessResponse:
        """
        Deactivate user account (soft delete).
        
        Args:
            user_id: User's ID
            password: Password confirmation
            
        Raises:
            UserNotFoundError: If user doesn't exist
            InvalidPasswordError: If password is incorrect
        """
        try:
            with create_user_repository() as user_repo:
                user = user_repo.get_user_by_id(user_id)
                if not user:
                    raise UserNotFoundError(f"User {user_id} not found")

                if not self.password_manager.verify_password(password, user.hashed_password):
                    raise InvalidPasswordError("Password is incorrect")

                user_repo.deactivate_user(user_id)

                logger.info(f"User {user_id} account deactivated")

                return UserSuccessResponse(
                    success=True,
                    data=None
                )

        except (UserNotFoundError, InvalidPasswordError):
            raise
        except Exception as e:
            logger.error(f"Failed to deactivate user {user_id}: {e}", exc_info=True)
            raise RuntimeError(f"Account deactivation failed: {e}")

    def reactivate_account(self, email: str, password: str) -> UserSuccessResponse:
        """
        Reactivate a deactivated account.

        Args:
            email: User's email address
            password: Password for verification

        Returns:
            Reactivated user information

        Raises:
            UserNotFoundError: If user doesn't exist
            InvalidPasswordError: If password is incorrect
            UserAlreadyActiveError: If account is already active
        """
        try:
            with create_user_repository() as user_repo:
                user = user_repo.get_user_by_email(email)

                if not user:
                    raise UserNotFoundError("User not found")

                if user.is_active:
                    raise UserAlreadyActiveError("Account is already active")

                if not self.password_manager.verify_password(password, user.hashed_password):
                    raise InvalidPasswordError("Invalid password")

                # TODO: handle sending e-mail, this endpoint is only for testing

                reactivated = user_repo.reactivate_user(user.id)

                logger.info(f"User {user.id} account reactivated")

                user_response = UserResponse.model_validate(reactivated)
                return UserSuccessResponse(
                    success=True,
                    data=user_response
                )

        except (UserNotFoundError, InvalidPasswordError, UserAlreadyActiveError):
            raise
        except Exception as e:
            logger.error(f"Failed to reactivate account for {email}: {e}", exc_info=True)
            raise RuntimeError(f"Account reactivation failed: {e}")

    def delete_account(self, user_id: int, password: str) -> UserSuccessResponse:
        """
        Permanently delete user account (hard delete).
        
        Args:
            user_id: User's ID
            password: Password confirmation
            
        Raises:
            UserNotFoundError: If user doesn't exist
            InvalidPasswordError: If password is incorrect
        """
        try:
            with create_user_repository() as user_repo:
                user = user_repo.get_user_by_id(user_id)
                if not user:
                    raise UserNotFoundError(f"User {user_id} not found")

                if not self.password_manager.verify_password(password, user.hashed_password):
                    raise InvalidPasswordError("Password is incorrect")

                user_repo.delete_user(user_id)

                logger.info(f"User {user_id} account permanently deleted")

                return UserSuccessResponse(
                    success=True,
                    data=None
                )

        except (UserNotFoundError, InvalidPasswordError):
            raise
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}", exc_info=True)
            raise RuntimeError(f"Account deletion failed: {e}")
