{%- if cookiecutter.use_redis == 'yes' %}
"""
Redis Cache Adapter.
"""
from typing import Optional
import redis.asyncio as redis

from pkg.config.settings import settings
from internal.ports.repositories import CacheRepository


# Redis client
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection."""
    global redis_client
    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> redis.Redis:
    """Get Redis client."""
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client


class RedisCacheRepository(CacheRepository):
    """Redis implementation of CacheRepository."""
    
    def __init__(self, client: redis.Redis = None):
        self.client = client or get_redis()
    
    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        expire_seconds: Optional[int] = None,
    ) -> bool:
        if expire_seconds:
            await self.client.setex(key, expire_seconds, value)
        else:
            await self.client.set(key, value)
        return True
    
    async def delete(self, key: str) -> bool:
        result = await self.client.delete(key)
        return result > 0
    
    async def exists(self, key: str) -> bool:
        result = await self.client.exists(key)
        return result > 0
{%- else %}
"""Cache adapter placeholder (Redis not enabled)."""
{%- endif %}
