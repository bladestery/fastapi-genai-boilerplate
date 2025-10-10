"""Custom Swagger / ReDoc documentation setup with optional prefix."""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)


class CustomDocsService:
    """Custom Swagger / ReDoc documentation setup with optional prefix."""

    @staticmethod
    def setup_custom_docs(app: FastAPI, prefix: str | None = None) -> None:
        """Setup Swagger and ReDoc docs with optional prefix."""
        if prefix:
            swagger_path = f"/{prefix}/docs"
            redoc_path = f"/{prefix}/redocs"
            openapi_url = f"/{prefix}/openapi.json"

            # Override default openapi URL for prefixed docs
            @app.get(openapi_url, include_in_schema=False)
            async def openapi() -> Any:
                """Override default openapi URL for prefixed docs."""
                return app.openapi()

            @app.get(swagger_path, include_in_schema=False)
            async def custom_swagger_ui() -> Any:
                """Custom Swagger UI."""
                return get_swagger_ui_html(
                    openapi_url=openapi_url,
                    title=f"{prefix.upper()} API Docs",
                    oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                    swagger_js_url="/static/swagger-ui-bundle.js",
                    swagger_css_url="/static/swagger-ui.css",
                )

            @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
            async def swagger_ui_redirect() -> Any:
                """Swagger UI redirect."""
                return get_swagger_ui_oauth2_redirect_html()

            @app.get(redoc_path, include_in_schema=False)
            async def custom_redoc_ui() -> Any:
                """Custom ReDoc UI."""
                return get_redoc_html(
                    openapi_url=openapi_url,
                    title=f"{prefix.upper()} API ReDoc",
                    redoc_js_url="/static/redoc.standalone.js",
                )
