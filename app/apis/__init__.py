"""API Router Configuration"""

from fastapi import APIRouter

from app.core.config import settings

from .monitor.routers import monitor_router
from .v1 import v1_routers

# Initialize the main application router
api_routers = APIRouter()
api_routers.include_router(monitor_router, prefix="")
api_routers.include_router(v1_routers, prefix=f"/{settings.API_PREFIX}/api/v1")

__all__ = ["api_routers"]
