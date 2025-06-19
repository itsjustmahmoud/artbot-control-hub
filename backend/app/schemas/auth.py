"""
Request and response schemas for authentication endpoints.
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request schema."""
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    access_level: str = Field(..., description="User access level")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserInfo(BaseModel):
    """User information schema."""
    access_level: str = Field(..., description="User access level")
    expires_at: int = Field(..., description="Token expiration timestamp")


class LogoutResponse(BaseModel):
    """Logout response schema."""
    message: str = Field(default="Logged out successfully", description="Logout message")


class PermissionsResponse(BaseModel):
    """Permissions response schema."""
    access_level: str = Field(..., description="Access level")
    permissions: list[str] = Field(..., description="List of permissions")
