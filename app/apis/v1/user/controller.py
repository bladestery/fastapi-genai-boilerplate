"""Route for user"""

from fastapi import Depends, Request
from fastapi.routing import APIRouter
from fastapi_limiter.depends import RateLimiter
from fastapi_utils.cbv import cbv

from app.core.responses import AppJSONResponse

from .models import CreateUserRequest
from .service import UserService

router = APIRouter()


def common_dependency() -> dict[str, str]:
    """Common dependency."""

    return {"msg": "This is a dependency"}


@cbv(router)
class UserRoute:
    """User-related routes."""

    def __init__(self, common_dep=Depends(common_dependency)) -> None:
        self.common_dep = common_dep
        self.service = UserService()

    @router.post(
        "/user",
        response_class=AppJSONResponse,
        dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    )
    async def create_user(
        self, request: Request, request_params: CreateUserRequest
    ) -> AppJSONResponse:
        """Create a new user."""
        data, message, status_code = await self.service.create_user_service(
            request_params=request_params
        )
        return AppJSONResponse(data=data, message=message, status_code=status_code)
