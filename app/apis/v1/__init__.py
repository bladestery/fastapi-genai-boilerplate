"""Initialize API Routers"""

from fastapi import APIRouter

from .user.route import router as user_router

# Define and configure versioned API routers
v1_routers = APIRouter()
v1_routers.include_router(user_router, tags=["User"])

__all__ = ["v1_routers"]
