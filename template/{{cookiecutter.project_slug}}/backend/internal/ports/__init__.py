"""Ports package - Interfaces for external dependencies."""
from .repositories import UserRepository
{%- if cookiecutter.use_redis == 'yes' %}
from .repositories import CacheRepository
{%- endif %}

__all__ = [
    "UserRepository",
    {%- if cookiecutter.use_redis == 'yes' %}
    "CacheRepository",
    {%- endif %}
]
