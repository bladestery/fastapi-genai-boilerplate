"""User service"""

from typing import Any, Tuple

from .models import CreateUserRequest


class UserService:
    """User service."""

    def __init__(self) -> None:
        """Initialize the service."""
        pass

    async def create_user_service(
        self, request_params: CreateUserRequest
    ) -> Tuple[Any, str, int]:
        """Create a new user."""
        payload = {
            "user_id": 1,
            "name": request_params.name,
            "email": request_params.email,
        }
        message = "User created successfully"
        status_code = 201
        return payload, message, status_code
