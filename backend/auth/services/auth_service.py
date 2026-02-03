import logging

from backend.auth.schemas import LoginRequest, TokenResponse
from backend.security.jwt_manager import JWTManager
from backend.security.password_manager import PasswordManager
from backend.auth.exceptions import (
    InvalidCredentialsError,
    InactiveUserError,
)
from backend.accounts.factories.repositories import create_user_repository


logger = logging.getLogger(__name__)


class AuthService:
    """Handles authentication business logic."""
    
    def __init__(
        self,
        password_manager: PasswordManager,
        jwt_manager: JWTManager
    ) -> None:
        """
        Args:
            password_manager: Password hashing/verification
            jwt_manager: JWT token creation/verification
        """
        self.password_manager = password_manager
        self.jwt_manager = jwt_manager
    
    def authenticate_user(self, login_data: LoginRequest) -> TokenResponse:
        """
        Authenticate user and return access token.

        Args:
            login_data: Login credentials

        Returns:
            Token response with access token and expiration info

        Raises:
            InvalidCredentialsError: If email or password is incorrect
            InactiveUserError: If user account is inactive
        """
        try:
            with create_user_repository() as user_repo:
                user = user_repo.get_user_by_email(login_data.email)

                if not user:
                    raise InvalidCredentialsError("Incorrect email or password")

                if not self.password_manager.verify_password(
                    login_data.password,
                    user.hashed_password
                ):
                    raise InvalidCredentialsError("Incorrect email or password")

                if not user.is_active:
                    raise InactiveUserError("User account is inactive")

                token = self.jwt_manager.create_token(user.id, user.email)

                logger.info(f"User {user.email} authenticated successfully")

                return TokenResponse(
                    access_token=token,
                    token_type="bearer",
                    expires_in=self.jwt_manager.token_expire_hours * 3600
                )
        except (InvalidCredentialsError, InactiveUserError):
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise RuntimeError(f"Authentication failed: {e}")
    
    def get_current_user_id(self, token: str) -> int:
        """
        Extract user ID from token.

        Args:
            token: JWT token string

        Returns:
            User ID

        Raises:
            ExpiredTokenError: If token has expired
            InvalidTokenError: If token is invalid
        """
        payload = self.jwt_manager.verify_token(token)
        user_id = int(payload["sub"])
        return user_id
