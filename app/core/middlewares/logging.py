"""Logging middleware with request ID tracing."""

import contextvars
import uuid

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import AppEnvs, settings

# Global context variable to store request ID per request
request_id_ctx_var = contextvars.ContextVar("request_id", default=None)

# Determine the environment (e.g., development, production)
APP_ENV = settings.environment.lower()


def add_request_id_to_log(record: dict) -> None:
    """Inject the request ID into log records."""
    record["extra"]["request_id"] = request_id_ctx_var.get() or "N/A"


# Configure logger to use the request ID patch
logger.configure(patcher=add_request_id_to_log)

# Define log format
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "RequestID=<cyan>{extra[request_id]}</cyan> | "
    "<level>{message}</level>"
)

# Remove default log handler and add custom stream handler
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format=LOG_FORMAT,
    level=settings.log_level.upper(),
    enqueue=True,
    colorize=True,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log incoming HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Use incoming request ID or generate a new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Set request ID into context variable and request state
        request_id_ctx_var.set(request_id)  # type: ignore
        request.state.request_id = request_id

        try:
            # Log request body if running in non-production environments
            if APP_ENV in {AppEnvs.DEVELOPMENT, AppEnvs.QA, AppEnvs.DEMO}:
                body_bytes = await request.body()
                body_text = body_bytes.decode("utf-8", errors="ignore").strip()
                logger.debug(
                    f"📥 Request: {request.method} {request.url.path} | Body: {body_text or 'empty'}"
                )

            # Forward the request to the next handler (e.g., endpoint)
            response = await call_next(request)

        except Exception as e:
            logger.exception(
                f"❌ Error while processing {request.method} {request.url.path}: {str(e)}"
            )
            raise

        # Add the request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response
