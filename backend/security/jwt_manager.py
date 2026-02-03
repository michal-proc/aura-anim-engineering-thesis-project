import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from backend.security.exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
)


logger = logging.getLogger(__name__)


class JWTManager:
    """Handles JWT token creation and validation."""
    
    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str = "HS256",
        token_expire_hours: int = 24
    ):
        """
        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT signing algorithm
            token_expire_hours: Token expiration time in hours
        """
        self.secret_key = secret_key or self._get_secret_key()
        self.algorithm = algorithm
        self.token_expire_hours = token_expire_hours
    
    def _get_secret_key(self) -> str:
        """Get secret key from environment or generate a default one."""
        key = os.getenv("JWT_SECRET_KEY")
        if not key:
            # Development setup
            import secrets
            key = secrets.token_urlsafe(32)
            logger.warning("WARNING: Using generated JWT secret key. Set JWT_SECRET_KEY in production!")
        return key
    
    def create_token(self, user_id: int, email: str) -> str:
        """
        Create a JWT token for a user.

        Args:
            user_id: User's ID
            email: User's email

        Returns:
            Encoded JWT token string
        """
        expire = datetime.now(timezone.utc) + timedelta(hours=self.token_expire_hours)
        payload = {
            # Standard JWT claims
            "sub": str(user_id),  # Subject: identifies the user
            "exp": expire,        # Expiration: when the token becomes invalid
            "iat": datetime.now(timezone.utc),  # Issued At: when token was created

            # Custom claims
            "email": email  # User's email
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string to verify

        Returns:
            Decoded token payload

        Raises:
            ExpiredTokenError: If token has expired
            InvalidTokenError: If token signature is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError as e:
            raise ExpiredTokenError("Token has expired") from e
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError("Invalid token") from e
