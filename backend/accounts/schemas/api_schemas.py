from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserCreateRequest(BaseModel):
    """User registration request."""

    email: EmailStr = Field(description="User email address")
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Username (3-50 characters, alphanumeric and underscores only)"
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)"
    )
    full_name: str | None = Field(
        None,
        max_length=255,
        description="Full name (optional)"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v


class UserResponse(BaseModel):
    """User information response (without password)."""

    id: int
    email: str
    username: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserSuccessResponse(BaseModel):
    """Generic success response wrapper."""

    success: bool = Field(description="Whether the operation was successful", default=True)
    data: UserResponse | None = Field(
        description="Payload of the successful operation",
        default=None,
    )


class UserUpdateRequest(BaseModel):
    """User profile update request."""

    email: EmailStr | None = Field(None, description="New email address")
    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        description="New username"
    )
    full_name: str | None = Field(None, max_length=255, description="New full name")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """Validate username format."""
        if v is not None and not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v


class PasswordChangeRequest(BaseModel):
    """Password change request."""

    current_password: str = Field(description="Current password")
    new_password: str = Field(
        min_length=8,
        max_length=100,
        description="New password (minimum 8 characters)"
    )


class AccountDeletionRequest(BaseModel):
    """Account deletion request."""

    password: str = Field(description="Password for account deletion verification")


class AccountReactivationRequest(BaseModel):
    """Account reactivation request"""

    email: EmailStr = Field(description="User email address")
    password: str = Field(description="Password for verification")


class ForgotPasswordRequest(BaseModel):
    """Password reset request (forgot password)."""

    email: EmailStr = Field(description="User email address")


class PasswordResetRequest(BaseModel):
    """Password reset with token request."""

    token: str = Field(
        description="Password reset token (not validated in this simulation)"
    )
    email: EmailStr = Field(description="User email address")
    new_password: str = Field(
        min_length=8,
        max_length=100,
        description="New password (minimum 8 characters)",
    )
