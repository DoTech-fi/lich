"""
Pydantic request schemas for API validation.
All input must be validated here before reaching services.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateUserRequest(BaseModel):
    """Request schema for user creation."""
    
    email: EmailStr
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    password: str = Field(..., min_length=8, max_length=100)
    {%- endif %}
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Ensure password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    {%- endif %}
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format."""
        if v is None:
            return v
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.lower()


class UpdateUserRequest(BaseModel):
    """Request schema for user update."""
    
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.lower()


{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}


class LoginRequest(BaseModel):
    """Request schema for user login."""
    
    email: EmailStr
    password: str = Field(..., min_length=1)


class ChangePasswordRequest(BaseModel):
    """Request schema for password change."""
    
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""
    
    refresh_token: str
{%- endif %}
