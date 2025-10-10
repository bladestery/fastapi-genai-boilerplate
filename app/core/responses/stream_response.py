"""Response module for application-level streaming API responses."""

from collections.abc import AsyncGenerator, Callable
from typing import Any

from fastapi.responses import StreamingResponse


class AppStreamingResponse(StreamingResponse):
    """Custom streaming response for the entire application.

    This wraps an async generator into a streaming HTTP response,
    allowing large or continuous data to be sent efficiently.
    """

    def __init__(
        self,
        data_stream: Callable[[], AsyncGenerator[Any]] | AsyncGenerator[Any],
        status_code: int = 200,
    ):
        """
        Args:
            data_stream (AsyncGenerator or Callable): A generator that yields streamable data chunks.
            status_code (int): HTTP status code.
        """
        # Ensure the stream is callable for consistent execution
        generator = data_stream() if callable(data_stream) else data_stream

        super().__init__(
            content=generator,
            media_type="text/event-stream",
            status_code=status_code,
        )
