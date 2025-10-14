"""Primary application entry point for FastAPI Boilerplate."""

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from app.apis import api_routers
from app.apis.monitor.routers import MonitorRoutes
from app.core.config import settings
from app.core.enums import AppEnvs
from app.core.exceptions import HandleExceptions
from app.core.lifespan import lifespan
from app.core.middlewares import RequestContextMiddleware, RequestIDMiddleware


def configure_middleware() -> list[Middleware]:
    """Define and return middleware settings."""
    return [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(RequestIDMiddleware),
        Middleware(RequestContextMiddleware),
    ]


def configure_routes(app: FastAPI) -> None:
    """Attach API routes to the application."""
    app.include_router(api_routers)

    # Include monitoring endpoints
    if AppEnvs.PRODUCTION != settings.ENVIRONMENT:
        MonitorRoutes.setup_docs(app, prefix=settings.API_PREFIX)

    if AppEnvs.PRODUCTION == settings.ENVIRONMENT:
        MonitorRoutes.disable_docs(app)


def configure_metrics(app: FastAPI) -> None:
    """Instrument and expose Prometheus metrics."""
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        excluded_handlers=[],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)


def build_app() -> FastAPI:
    """Initialize and configure the FastAPI app instance."""
    app_instance = FastAPI(
        title="FastAPI Boilerplate",
        description="FastAPI project template.",
        version=settings.RELEASE_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        middleware=configure_middleware(),
        lifespan=lifespan,
    )

    HandleExceptions(app=app_instance)
    configure_routes(app_instance)
    configure_metrics(app_instance)

    app_instance.mount("/static", StaticFiles(directory="static"), name="static")

    return app_instance


app = build_app()
