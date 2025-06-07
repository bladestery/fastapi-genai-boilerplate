"""Application lifecycle management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from .middlewares import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    logger.info("🚀 Application starting up...")
    app.state.limiter = limiter
    yield
    logger.info("👋 Application shutting down...")
