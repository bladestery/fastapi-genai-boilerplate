"""Middleware for request context and request ID management."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.extra.logger import logger, request_id_ctx_var


# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a unique request ID (UUID4) per incoming HTTP request.

    The request ID is stored in a ContextVar and automatically bound to all log entries
    emitted during the request lifecycle. It is also attached to the response headers
    under the `X-Request-ID` key.

    This middleware improves traceability across distributed systems.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Generate and attach request ID, and propagate through logging context."""
        request_id = str(uuid.uuid4())
        request_id_ctx_var.set(request_id)

        # Add request_id to log context
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)

        # Include in response headers for client correlation
        response.headers["X-Request-ID"] = request_id
        return response


# Request Context Middleware
class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware that attaches useful request context (body, query, path, method) to request.state.

    This allows later components (logging, tracing, validation, etc.) to easily access
    the raw request body without consuming the stream.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Read and preserve the request body for downstream usage."""
        try:
            body_bytes = await request.body()
        except Exception:
            body_bytes = b""

        # Attach decoded body to state
        try:
            request.state.body = body_bytes.decode("utf-8") if body_bytes else None
        except UnicodeDecodeError:
            request.state.body = None

        # Recreate request with preserved body (important for downstream handlers)
        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        new_request = Request(request.scope, receive=receive)
        return await call_next(new_request)
