# 🛡️ Rate Limiting with SlowAPI

This project integrates request rate limiting using [**SlowAPI**](https://slowapi.readthedocs.io/), a lightweight and extensible rate limiter built specifically for FastAPI. It helps defend your API against abuse, brute force attacks, and accidental overloads.

---

## 🚀 Features

* IP-based or custom key-based rate limiting
* Flexible and declarative usage with decorators
* Global or per-route rate limits
* Automatic `429 Too Many Requests` handling
* Rate limit headers (e.g. `X-RateLimit-Remaining`, `Retry-After`) for client-side awareness

---

## 🔧 Installation

`SlowAPI` is already included in your project dependencies via `pyproject.toml`:

> ✅ No additional setup is needed if you're using the boilerplate.

---

## ⚙️ Configuration

The rate limiter is typically initialized in your middleware layer, e.g. in `app/core/middlewares/rate_limiter.py`:

```python
"""Rate limiter configuration and middleware exports."""

from fastapi import Request
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


def token_or_ip_key(request: Request) -> str:
    """Use Bearer token if available, else fallback to IP address."""
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        if token:
            return token
    # Fallback to IP address
    return get_remote_address(request)


# Create a limiter instance with custom key function
limiter = Limiter(key_func=token_or_ip_key)
```

---

## 🧩 Usage

### 📌 Apply Global Rate Limit

Add decorators to endpoints to enforce limits:

```python
@app.get("/ping")
@limiter.limit("10/minute")
async def ping():
    return {"message": "pong"}
```

### 🎯 Per Route Rate Limits

You can customize the limit per endpoint:

```python
@router.get("/secure-endpoint")
@limiter.limit("5/minute")
async def secure_data():
    return {"message": "Only 5 requests allowed per minute."}
```

### 🧠 Custom Key Functions

Use request headers or tokens to identify unique clients:

```python
def custom_key_func(request: Request):
    return request.headers.get("X-API-KEY") or get_remote_address(request)

limiter = Limiter(key_func=custom_key_func)
```

---

## 🚨 Handling Abuse Gracefully

* Customize the `RateLimitExceeded` handler for better error messaging
* Log blocked requests for auditing or alerting
* Adjust rate limits based on the route sensitivity or user role

---

## ✅ Best Practices

* Set stricter limits on login or write-heavy routes
* Use descriptive error messages on `429` responses
* Add retry headers (`Retry-After`) to help clients recover
* Monitor metrics and logs for rate limit events

---

## 📚 References

* 📘 [SlowAPI Documentation](https://slowapi.readthedocs.io/)
