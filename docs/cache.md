# 🧠 Redis Caching

This project uses **Redis** (via `aiocache`) for request-level caching, background task result storage, and general performance boosts.

---

## ✅ Features

* 🔄 **Redis backend** powered by `aiocache`
* 📦 **JSON serialization**
* 🕒 **TTL (Time-to-Live)** support
* 🧱 **Namespace isolation**
* 🔐 **Password-protected Redis support**
* 🧪 Fully async + compatible with FastAPI

---

## ⚙️ Configuration Example

Caching is configured in `app/core/cache/cache.py`:

```python
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from app.core.config import settings

cache = Cache(
    cache_class=Cache.REDIS,
    endpoint=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    ttl=300,
    namespace="fastapi_cache",
    serializer=JsonSerializer(),
    db=1,
)
```

Ensure you define Redis credentials in `.env`:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=yourpassword
```

---

## 🔐 Security Tips

* Use **auth-enabled Redis** in production (with `REDIS_PASSWORD`)
* Use **namespace** to separate caching use cases
* Prevent brute-force cache key flooding:

  * Normalize requests (e.g., sorted query params)
  * Use hashed cache keys via `hashlib`

---

## 🐳 Docker Redis Setup

Redis and RedisInsight are included in `docker-compose.yml`:

| Service      | URL                                            | Port |
| ------------ | ---------------------------------------------- | ---- |
| Redis        | redis\://localhost:6379                        | 6379 |
| RedisInsight | [http://localhost:8001](http://localhost:8001) | 8001 |

---

## 🧪 Sample Usage

```python
from app.core.cache.cache import cache

@router.get("/cached")
async def get_cached_response():
    result = await cache.get("my_cache_key")
    if result:
        return {"cached": True, "data": result}

    # expensive logic
    result = expensive_function()
    await cache.set("my_cache_key", result)
    return {"cached": False, "data": result}
```

---

## 📚 References

* [aiocache Docs](https://aiocache.readthedocs.io/)
* [RedisInsight](https://redis.com/redis-enterprise/redis-insight/)
* [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
