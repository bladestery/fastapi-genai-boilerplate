"""User controller"""

from .request import CreateUserRequest
from .response import UserJSONResponse
from .service import UserService


class UserController:
    """User controller."""

    def __init__(self) -> None:
        """Initialize the controller."""
        pass

    async def get_user_controller(self, user_id: int) -> UserJSONResponse:
        """Retrieve user details."""
        payload, message, status_code = await UserService().get_user_service(
            user_id=user_id
        )
        return UserJSONResponse(
            payload=payload, message=message, status_code=status_code
        )

    async def create_user_controller(self, request_params: CreateUserRequest):
        """Create a new user."""
        payload, message, status_code = {}, "User created successfully", 201
        return UserJSONResponse(
            payload=payload, message=message, status_code=status_code
        )
