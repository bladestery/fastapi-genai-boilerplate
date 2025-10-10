"""Monitoring endpoints: root redirect, health check, logger control, Prometheus metrics, and custom API docs."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI, Request, Response, status
from fastapi.responses import RedirectResponse
from loguru import logger
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.apis.monitor.service import CustomDocsService
from app.core.config import settings
from app.core.extra.logger import configure_logger
from app.core.responses import AppJSONResponse

from .models import LoggerLevelRequestParams

# Router initialization
monitor_router = APIRouter(
    prefix="",
    tags=["Monitor"],
    redirect_slashes=True,
)


# Class-based API routes
class MonitorRoutes:
    """Monitoring endpoints for system health, logging, metrics, and documentation."""

    # Root Redirect
    @staticmethod
    @monitor_router.get(
        "/",
        summary="Redirect to API docs",
        description="Redirects `/` to the interactive API documentation at `/docs`.",
        response_class=RedirectResponse,
        status_code=status.HTTP_302_FOUND,
    )
    async def root() -> RedirectResponse:
        """Redirect requests from `/` to `/docs`."""
        return RedirectResponse(url="/docs")

    # Health Check
    @staticmethod
    @monitor_router.get(
        "/health",
        summary="Service Health",
        description="Returns basic health and version info of the running service.",
        response_description="Health status and version",
        response_class=AppJSONResponse,
        status_code=status.HTTP_200_OK,
    )
    async def health() -> AppJSONResponse:
        """Simple service health endpoint for readiness probes."""
        return AppJSONResponse(
            data={
                "version": settings.RELEASE_VERSION,
                "environment": settings.ENVIRONMENT.value,
            },
            message="Service is up and running.",
            status="success",
            status_code=status.HTTP_200_OK,
        )

    # Dynamic Log Level
    @staticmethod
    @monitor_router.post(
        "/logger",
        summary="Update Logger Level",
        description="Change the global logger level dynamically without restart.",
        response_class=AppJSONResponse,
        response_description="Updated log level confirmation",
        status_code=status.HTTP_200_OK,
    )
    async def update_log_level(
        request: Request,
        request_params: LoggerLevelRequestParams,
    ) -> AppJSONResponse:
        """Update the log level dynamically (useful for debugging production issues)."""
        try:
            new_level = request_params.log_level.value
            configure_logger(new_level)
            logger.success(f"Updated global log level to `{new_level}`")
            return AppJSONResponse(
                data={"current_log_level": new_level},
                message=f"Log level successfully updated to {new_level}",
                status="success",
                status_code=status.HTTP_200_OK,
            )
        except Exception as exc:
            logger.exception(f"Failed to update log level: {exc}")
            return AppJSONResponse(
                data=None,
                message=f"Error updating log level: {exc}",
                status="error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Docs Setup
    @staticmethod
    def setup_docs(app: FastAPI, prefix: str | None = None) -> None:
        """Register Swagger and ReDoc documentation (with optional prefix)."""
        CustomDocsService.setup_custom_docs(app, prefix)

    @staticmethod
    def disable_docs(app: FastAPI) -> None:
        """Disable all documentation routes (used in production environments)."""

        async def disabled_docs() -> AppJSONResponse:
            return AppJSONResponse(
                status="error",
                message=(
                    "API documentation is disabled in this environment. "
                    "Please contact the engineering team for access."
                ),
                data=None,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Disable standard doc URLs
        disabled_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            f"/{settings.API_PREFIX}/docs",
            f"/{settings.API_PREFIX}/redoc",
            f"/{settings.API_PREFIX}/openapi.json",
        ]

        for path in disabled_paths:
            app.add_api_route(path, disabled_docs, methods=["GET"], tags=["Monitor"])

    # Prometheus Metrics
    @staticmethod
    @monitor_router.get(
        "/metrics",
        summary="Prometheus Metrics",
        description="Exposes application metrics for Prometheus scraping.",
        include_in_schema=False,
    )
    async def metrics() -> Response:
        """Expose Prometheus-formatted metrics."""
        try:
            metrics_data = generate_latest()
            return Response(
                content=metrics_data,
                media_type=CONTENT_TYPE_LATEST,
                headers={"Cache-Control": "no-store"},
            )
        except Exception as exc:
            logger.exception(f"Failed to generate metrics: {exc}")
            return Response(
                content=b"metrics_unavailable 1\n",
                media_type="text/plain; version=0.0.4",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
