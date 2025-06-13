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


__all__ = ["limiter", "SlowAPIMiddleware"]
