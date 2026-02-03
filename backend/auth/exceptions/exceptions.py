"""Custom exceptions for authentication."""


class AuthenticationError(Exception):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are incorrect."""
    pass


class InactiveUserError(AuthenticationError):
    """Raised when user account is inactive."""
    pass


class UserNotFoundError(AuthenticationError):
    """Raised when user cannot be found."""
    pass
