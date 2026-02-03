"""Custom exceptions for application security."""


class SecurityError(Exception):
    """Base exception for security-related errors."""
    pass


class InvalidTokenError(SecurityError):
    """Raised when token signature is invalid or malformed."""
    pass


class ExpiredTokenError(SecurityError):
    """Raised when token has expired."""
    pass
