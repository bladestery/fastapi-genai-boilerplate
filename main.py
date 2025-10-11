"""Application entrypoint for running FastAPI in local or production environments."""

from __future__ import annotations

import multiprocessing
import sys

import uvicorn
from loguru import logger

from app.core.config import settings


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


# ---------------- Entrypoint ---------------- #
def main() -> None:
    """Entry point to start the FastAPI application."""
    env_value = settings.ENVIRONMENT

    #if env_value == AppEnvs.LOCAL:
    #    run_local()
    #else:
    #    run_prod()
    run_local()

if __name__ == "__main__":
    main()
