"""Chat service"""

import asyncio
import hashlib
import json
from typing import AsyncGenerator, Callable

from loguru import logger

from app import cache, trace

from .models import ChatRequest


class ChatService:
    """Service for handling chat logic."""

    def __init__(self) -> None:
        """Initialize the chat service."""

    @staticmethod
    def _hash_request(payload: dict) -> str:
        """Generate a unique cache key from request payload."""
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    @trace(name="chat_service")
    async def chat_service(
        self, request_params: ChatRequest
    ) -> Callable[[], AsyncGenerator[str, None]]:
        """
        Return a streaming chat generator.
        If the response is cached, replay the cached stream.
        Otherwise, generate the stream and cache the result.
        """
        payload = request_params.model_dump()
        cache_key = self._hash_request(payload)
        logger.debug(f"Generated cache key: {cache_key}")

        cached_response = await cache.get(cache_key)
        if cached_response:
            logger.info("Cache hit. Replaying cached response.")

            async def replay_cached_stream() -> AsyncGenerator[str, None]:
                for chunk in cached_response.split("\n\n"):
                    yield chunk + "\n\n"

            return replay_cached_stream

        logger.info("Cache miss. Generating new response stream.")

        async def stream() -> AsyncGenerator[str, None]:
            buffer = ""
            for i in range(request_params.number):
                chunk = f"event: content\ndata: {i}\n\n"
                logger.debug(f"Streaming chunk: {chunk.strip()}")

                buffer += chunk
                yield chunk
                await asyncio.sleep(request_params.sleep)

            chunk = "event: complete\ndata: [DONE]\n\n"
            logger.debug("Streaming complete chunk.")
            buffer += chunk
            yield chunk

            await cache.set(cache_key, buffer)
            logger.info(f"Response cached under key: {cache_key}")

        return stream
