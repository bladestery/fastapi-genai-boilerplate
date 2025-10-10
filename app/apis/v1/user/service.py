"""User service"""

from typing import Any

from .models import CreateUserRequest


class UserService:
    """User service."""

    def __init__(self) -> None:
        """Initialize the service."""
        pass

    async def sample_function(self, temp_arg: str) -> str:
        """Convert input string to uppercase."""
        return temp_arg.upper()

    async def create_user_service(
        self, request_params: CreateUserRequest
    ) -> tuple[Any, str, int]:
        """Create a new user from request parameters."""
        await self.sample_function(temp_arg=request_params.name)

        payload = {
            "user_id": 1,
            "name": request_params.name,
            "email": request_params.email,
        }
        message = "User created successfully"
        status_code = 201
        return payload, message, status_code
