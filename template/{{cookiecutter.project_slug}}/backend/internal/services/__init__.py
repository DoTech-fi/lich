"""Services package - Business logic."""
from .user_service import UserService
from .auth_deps import (
    get_user_service,
    get_current_user,
    get_current_active_user,
    get_admin_user,
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    create_access_token,
    create_refresh_token,
    {%- endif %}
)

__all__ = [
    "UserService",
    "get_user_service",
    "get_current_user",
    "get_current_active_user",
    "get_admin_user",
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    "create_access_token",
    "create_refresh_token",
    {%- endif %}
]
