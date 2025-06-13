"""Chat service"""

import asyncio
from typing import AsyncGenerator, Callable

from app import trace

from .models import ChatRequest


class ChatService:
    """Service for handling chat logic."""

    def __init__(self) -> None:
        """Initialize the chat service."""
        pass

    @trace(name="chat_service")
    async def chat_service(
        self, request_params: ChatRequest
    ) -> Callable[[], AsyncGenerator[str, None]]:
        """Return a streaming chat generator."""

        async def stream() -> AsyncGenerator[str, None]:
            for i in range(request_params.number):
                yield f"event: content\ndata: {i}\n\n"
                await asyncio.sleep(request_params.sleep)

            yield "event: complete\ndata: [DONE]\n\n"

        return stream
