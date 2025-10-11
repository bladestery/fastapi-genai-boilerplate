"""Application entrypoint for running FastAPI in local or production environments."""

from __future__ import annotations

import multiprocessing
import sys
from typing import Any

import uvicorn
from fastapi import FastAPI
from gunicorn.app.base import BaseApplication
from loguru import logger

from app.core.config import settings
from app.core.enums import AppEnvs
from app.core.server import app


# ---------------- Utility ---------------- #
def calculate_worker_count() -> int:
    """Calculate optimal number of Gunicorn workers."""
    return multiprocessing.cpu_count() * 2 + 1


# ---------------- Local ---------------- #
def run_local() -> None:
    """Run FastAPI app locally with auto-reload."""
    logger.info("🚀 Starting FastAPI in LOCAL development mode.")
    try:
        uvicorn.run(
            "app.core.server:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            workers=1,
            env_file=settings.ENV_FILE,
        )
    except Exception as exc:
        logger.exception(f"Uvicorn failed to start in local mode: {exc}")
        sys.exit(1)


# ---------------- Gunicorn ---------------- #
class GunicornApp(BaseApplication):
    """Custom Gunicorn application to run FastAPI with Uvicorn workers."""

    def __init__(
        self,
        app: FastAPI,
        host: str,
        port: int,
        workers: int | None = None,
    ) -> None:
        self.application = app
        self.host = host
        self.port = port
        self.workers = workers or calculate_worker_count()
        super().__init__()

    def load_config(self) -> None:
        """Configure Gunicorn runtime settings."""
        config: dict[str, Any] = {
            "bind": f"{self.host}:{self.port}",
            "workers": self.workers,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "accesslog": "-",  # stdout
            "errorlog": "-",  # stderr
            "loglevel": settings.LOG_LEVEL.value.lower(),
            "timeout": 60,
            "graceful_timeout": 30,
            "keepalive": 5,
            "preload_app": True,
        }
        for key, value in config.items():
            self.cfg.set(key, value)

    def load(self) -> FastAPI:
        """Return the FastAPI application instance."""
        return self.application


# ---------------- Production ---------------- #
def run_prod() -> None:
    """Run FastAPI app in production with Gunicorn."""
    workers = settings.WORKER_COUNT or calculate_worker_count()
    env_name = settings.ENVIRONMENT.value

    logger.info(f"🚀 Starting FastAPI in {env_name.upper()} mode (workers={workers})")

    try:
        GunicornApp(
            app=app,
            host=settings.HOST,
            port=settings.PORT,
            workers=workers,
        ).run()
    except Exception as exc:
        logger.exception(f"Gunicorn failed to start in {env_name} mode: {exc}")
        sys.exit(1)


# ---------------- Entrypoint ---------------- #
def main() -> None:
    """Entry point to start the FastAPI application."""
    env_value = settings.ENVIRONMENT

    if env_value == AppEnvs.LOCAL:
        run_local()
    else:
        run_prod()


if __name__ == "__main__":
    main()
