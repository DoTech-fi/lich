"""
Pydantic response schemas.
Never expose internal entities directly - use these DTOs.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class UserResponse(BaseModel):
    """Response schema for user data."""
    
    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    full_name: str
    role: str
    status: str
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Response schema for user list."""
    
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class LoginResponse(BaseModel):
    """Response schema for successful login."""
    
    user: UserResponse
    tokens: TokenResponse
{%- endif %}


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Resource not found",
                    "details": {}
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    service: str
    version: str = "1.0.0"
