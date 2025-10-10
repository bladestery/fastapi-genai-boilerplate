"""Simple cache setup using aiocache with support for Redis and in-memory backends."""

from aiocache import Cache
from aiocache.serializers import JsonSerializer

from app.core.config import settings
from app.core.enums import CacheBackend

if settings.CACHE_BACKEND == CacheBackend.REDIS:
    cache = Cache(
        cache_class=Cache.REDIS,
        endpoint=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        ttl=300,  # Time-To-Live: 300 seconds
        namespace="fastapi_cache",
        serializer=JsonSerializer(),
        db=1,
    )
elif settings.CACHE_BACKEND == CacheBackend.LOCAL:
    cache = Cache(
        cache_class=Cache.MEMORY,  # In-memory cache
        ttl=300,
        namespace="fastapi_cache",
        serializer=JsonSerializer(),
    )
else:
    raise ValueError(f"Unsupported cache backend: {settings.CACHE_BACKEND}")
