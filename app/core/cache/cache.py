"""Simple in-memory caching setup using aiocache."""

from aiocache import Cache
from aiocache.serializers import JsonSerializer

from app.core.config import settings

# Redis cache setup
cache = Cache(
    cache_class=Cache.REDIS,  # type: ignore
    endpoint=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    ttl=300,  # Time-To-Live: 300 seconds (3 minutes)
    namespace="fastapi_cache",
    serializer=JsonSerializer(),
    db=1,
)
