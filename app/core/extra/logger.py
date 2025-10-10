"""Global logging configuration with request ID and structured format."""

import sys
from contextvars import ContextVar

from loguru import logger

from app.core.config import settings
from app.core.enums import AppEnvs

# Context variable to store request_id per request
request_id_ctx_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def configure_logger(level: str | None = None) -> None:
    """Configure global logger with structured format."""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "request_id={extra[request_id]} | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level=(level or settings.LOG_LEVEL.value).upper(),
        backtrace=True,
        diagnose=settings.ENVIRONMENT.value == AppEnvs.LOCAL.value,
        enqueue=settings.ENVIRONMENT.value
        in {AppEnvs.PRODUCTION.value, AppEnvs.QA.value, AppEnvs.DEMO.value},
    )

    # Bind default request_id so it always exists
    logger.configure(extra={"request_id": "N/A"})


# Initialize global logger
configure_logger()


__all__ = ["logger", "configure_logger", "request_id_ctx_var"]
