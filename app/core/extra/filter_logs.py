"""Production-grade Uvicorn access log filtering utilities."""

from __future__ import annotations

import logging
import threading

from app.core.config import settings


class UvicornAccessLogFilter(logging.Filter):
    """Filter out Uvicorn access logs for specific paths (e.g., `/health`, `/metrics`)."""

    def __init__(self, skip_paths: list[str] | None = None) -> None:
        """Initialize the filter with paths to skip."""
        super().__init__()
        self._lock = threading.Lock()
        self.skip_paths: set[str] = set(skip_paths or [])

    def update_skip_paths(self, new_paths: list[str]) -> None:
        """Thread-safe method to update the skip paths at runtime."""
        with self._lock:
            self.skip_paths.update(new_paths)

    def filter(self, record: logging.LogRecord) -> bool:
        """Decide whether a log record should be emitted."""
        msg = record.getMessage()
        # Access log format: 'IP - "METHOD PATH HTTP/1.1" STATUS'
        try:
            path = msg.split('"')[1].split(" ")[1]  # Extract PATH
        except Exception:
            return True  # If format unexpected, don't filter
        return path not in self.skip_paths


# Filter setup helper
def setup_uvicorn_access_logs(skip_paths: list[str]) -> None:
    """Attach a Uvicorn access log filter to suppress specific noisy endpoints.

    This is useful for hiding routine health checks or metrics requests from logs
    (e.g., `/health`, `/metrics`, `/ready`).

    Example:
        setup_uvicorn_access_logs(["/health", "/metrics"])
    """
    access_logger = logging.getLogger("uvicorn.access")

    # Avoid attaching duplicate filters on re-init
    existing_filter = next(
        (f for f in access_logger.filters if isinstance(f, UvicornAccessLogFilter)),
        None,
    )
    if existing_filter:
        existing_filter.update_skip_paths(skip_paths)
        return

    access_logger.addFilter(UvicornAccessLogFilter(skip_paths))


setup_uvicorn_access_logs(
    skip_paths=[
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        f"/{settings.API_PREFIX}/docs",
        f"/{settings.API_PREFIX}/redoc",
        f"/{settings.API_PREFIX}/openapi.json",
        f"/{settings.API_PREFIX}/health",
    ]
)
