"""Route for user"""

from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi_utils.cbv import cbv

from .controller import UserController
from .request import CreateUserRequest
from .response import UserJSONResponse

router = APIRouter()


def common_dependency():
    """Common dependency."""

    return {"msg": "This is a dependency"}


@cbv(router)
class UserRoute:
    """User-related routes."""

    def __init__(self, common_dep=Depends(common_dependency)):
        self.common_dep = common_dep

    @router.get("/user/{user_id}", response_class=UserJSONResponse)
    async def get_user(self, user_id: int):
        """Retrieve user details."""
        return await UserController().get_user_controller(user_id=user_id)

    @router.post("/user", response_class=UserJSONResponse)
    async def create_user(self, request_params: CreateUserRequest):
        """Create a new user."""
        return await UserController().create_user_controller(
            request_params=request_params
        )
