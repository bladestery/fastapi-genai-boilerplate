"""Initialize extra modules."""

from .filter_logs import setup_uvicorn_access_logs

__all__ = [
    "setup_uvicorn_access_logs",
]
