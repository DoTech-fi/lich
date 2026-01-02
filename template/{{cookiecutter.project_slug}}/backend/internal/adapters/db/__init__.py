"""DB adapters package."""
from .connection import init_db, get_session
from .models import *
{%- if cookiecutter.database == 'postgresql' %}
from .user_repo import SQLAlchemyUserRepository
{%- else %}
from .user_repo import BeanieUserRepository
{%- endif %}

__all__ = [
    "init_db",
    "get_session",
    {%- if cookiecutter.database == 'postgresql' %}
    "SQLAlchemyUserRepository",
    {%- else %}
    "BeanieUserRepository",
    {%- endif %}
]
