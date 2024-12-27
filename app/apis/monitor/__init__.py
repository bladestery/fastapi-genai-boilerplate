from fastapi import APIRouter

from .health import health_router
from .root import root_router

monitor_router = APIRouter()

# Include routers for health endpoints and root endpoint
monitor_router.include_router(health_router, prefix="/health", tags=["Default"])
monitor_router.include_router(root_router, tags=["Default"])

__all__ = ["monitor_router"]
