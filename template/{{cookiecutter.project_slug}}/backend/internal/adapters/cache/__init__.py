"""Cache adapters package."""
{%- if cookiecutter.use_redis == 'yes' %}
from .redis_cache import init_redis, close_redis, get_redis, RedisCacheRepository

__all__ = ["init_redis", "close_redis", "get_redis", "RedisCacheRepository"]
{%- endif %}
