"""Account management exceptions."""


class AccountError(Exception):
    """Base exception for account errors."""
    pass


class UserAlreadyExistsError(AccountError):
    """Raised when user already exists."""
    pass


class UserNotFoundError(AccountError):
    """Raised when user is not found."""
    pass


class InvalidUsernameError(AccountError):
    """Raised when username is invalid."""
    pass


class InvalidPasswordError(AccountError):
    """Raised when password is invalid."""
    pass


class AccountDeactivatedError(AccountError):
    """Raised when attempting to use a deactivated account."""
    pass


class UserAlreadyActiveError(AccountError):
    """Raised when attempting to reactivate an already active account."""
