"""DTO package - Data Transfer Objects."""
from .requests import CreateUserRequest, UpdateUserRequest
{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
from .requests import LoginRequest, ChangePasswordRequest, RefreshTokenRequest
{%- endif %}
from .responses import (
    UserResponse,
    UserListResponse,
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    TokenResponse,
    LoginResponse,
    {%- endif %}
    MessageResponse,
    ErrorResponse,
    HealthResponse,
)

__all__ = [
    "CreateUserRequest",
    "UpdateUserRequest",
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    "LoginRequest",
    "ChangePasswordRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "LoginResponse",
    {%- endif %}
    "UserResponse",
    "UserListResponse",
    "MessageResponse",
    "ErrorResponse",
    "HealthResponse",
]
