"""Root router"""

from fastapi import APIRouter

from app import settings

from .response import RootResponse

root_router = APIRouter()


@root_router.get(
    "/",
    response_class=RootResponse,
    summary="Root",
    description="Endpoint of service (/)",
    response_description="JSON response indicating the root message of the service.",
)
async def root():
    """Endpoint for root."""
    return RootResponse(content={"message": "FastAPI Boilerplate", "version": settings.release_version}, status_code=200)
