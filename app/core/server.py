"""Primary application entry point"""

from typing import List

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from app.apis import api_routers
from app.core.config import settings
from app.core.exceptions import HandleExceptions
from app.core.lifespan import lifespan
from app.core.middlewares import LoggingMiddleware, SlowAPIMiddleware


def configure_routes(app: FastAPI) -> None:
    """Attach API routes to the application."""
    app.include_router(api_routers)


def configure_middleware() -> List[Middleware]:
    """Define and return middleware settings."""
    cors_middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(LoggingMiddleware),
        Middleware(SlowAPIMiddleware),
    ]
    return cors_middleware


def build_app() -> FastAPI:
    """Initialize and configure the FastAPI app instance."""
    app_instance = FastAPI(
        title="FastAPI Boilerplate",
        description="FastAPI project template.",
        version=settings.release_version,
        docs_url=None if settings.environment == "production" else "/docs",
        redoc_url=None if settings.environment == "production" else "/redoc",
        middleware=configure_middleware(),
        lifespan=lifespan,
    )

    # Register custom exception handlers
    HandleExceptions(app=app_instance)

    configure_routes(app=app_instance)
    return app_instance


app = build_app()
