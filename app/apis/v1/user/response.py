"""Response module for user API."""

from typing import Any

from fastapi.responses import JSONResponse


class UserJSONResponse(JSONResponse):
    """Custom JSON response for user API."""

    def __init__(
        self,
        payload: Any,
        message: str,
        status_code: int = 200,
    ):
        """Initialize the UserJSONResponse."""
        super().__init__(
            content={"message": message, "payload": payload},
            status_code=status_code,
            media_type="application/json",
        )
