"""Rate limiter configuration and middleware exports."""

from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

# Create a limiter instance
limiter = Limiter(key_func=get_remote_address)


__all__ = ["limiter", "SlowAPIMiddleware"]
