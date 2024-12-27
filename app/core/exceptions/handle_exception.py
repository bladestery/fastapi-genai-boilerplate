"""Exceptions"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app import logger
from app.constants import messages
from app.core.exceptions import CustomException


class HandleExceptions:
    """Handles various exception types for the FastAPI application."""

    def __init__(self, app: FastAPI):
        """Initializes exception handling."""
        self.app = app
        self._handle_custom_exception()
        self._handle_pydantic_exception()
        self._handle_fastapi_http_exception()
        self._handle_default_exception()

    def _handle_custom_exception(self):
        """Handle custom exceptions."""

        @self.app.exception_handler(CustomException)
        async def custom_exception_handler(request: Request, exc: CustomException):
            return await self._create_json_response(
                status_code=exc.status_code,
                message=exc.message,
                payload=exc.payload,
                error_log=exc.error_log,
            )

    def _handle_pydantic_exception(self):
        """Handle Pydantic validation errors."""

        @self.app.exception_handler(RequestValidationError)
        async def pydantic_exception_handler(
            request: Request, exc: RequestValidationError
        ):
            return await self._create_json_response(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message=messages.PYDANTIC_VALIDATION_ERROR,
                error_log=exc.errors(),  # type: ignore
            )

    def _handle_fastapi_http_exception(self):
        """Handle FastAPI HTTP exceptions."""

        @self.app.exception_handler(HTTPException)
        async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
            return await self._create_json_response(
                status_code=exc.status_code, message=exc.detail
            )

    def _handle_default_exception(self):
        """Handle all other exceptions."""

        @self.app.exception_handler(Exception)
        async def default_exception_handler(request: Request, exc: Exception):
            return await self._create_json_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=messages.INTERNAL_SERVER_ERROR,
            )

    async def _create_json_response(
        self, status_code: int, message: str, payload: Any = None, error_log: str = ""
    ) -> JSONResponse:
        """Create a JSON response for exceptions."""
        if error_log:
            logger.error(error_log)
        return JSONResponse(
            status_code=status_code,
            content={
                "payload": payload,
                "message": message,
                "status": status_code,
            },
        )
