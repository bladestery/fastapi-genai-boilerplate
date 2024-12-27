"""Health check router"""

from fastapi import APIRouter

from .response import HealthCheckResponse

health_router = APIRouter()


@health_router.get(
    "",
    response_class=HealthCheckResponse,
    summary="Service Health Check",
    description="Endpoint to check the health status of the service.",
    response_description="JSON response indicating the health status of the service.",
)
async def health():
    """Endpoint for health check."""
    return HealthCheckResponse(content={"check": "ok"}, status_code=200)
