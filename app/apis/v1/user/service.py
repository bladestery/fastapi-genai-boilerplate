"""User controller"""

from typing import Any, Dict, Tuple, Union

from .request import CreateUserRequest


class UserService:
    """User service."""

    def __init__(self) -> None:
        """Initialize the service."""
        pass

    async def get_user_service(self, user_id: int) -> Tuple[Any, str, int]:
        """Retrieve user details."""
        payload, message, status_code = {}, "User details retrieved successfully", 200
        return payload, message, status_code

    async def create_user_service(
        self, request_params: CreateUserRequest
    ) -> Union[Any, str, int]:
        """Create a new user."""
        payload, message, status_code = {}, "User created successfully", 201
        return payload, message, status_code
