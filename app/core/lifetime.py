"""Application lifecycle management"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")
