from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """User login credentials."""
    
    email: EmailStr = Field(
        description="User email address"
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="User password"
    )


class TokenResponse(BaseModel):
    """JWT token response after successful authentication."""
    
    access_token: str = Field(
        description="JWT access token"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type"
    )
    expires_in: int = Field(
        description="Token expiration in seconds"
    )
