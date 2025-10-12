"""Service helper for Retrieval-Augmented Generation pipelines."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import httpx
from loguru import logger

from app.services.vectorstores import VectorStoreService
from google import genai

__all__ = ["RagService", "RagServiceError"]


class RagServiceError(RuntimeError):
    """Raised when the RAG pipeline encounters an unrecoverable error."""


class RagService:
    """Coordinate embedding generation and vector database queries for RAG."""

    def __init__(
        self,
        *,
        vector_service: VectorStoreService,
        client: genai.client.AsyncClient,
        timeout: float = 10.0,
        default_top_k: int = 5,
    ) -> None:
        """Initialize the RAG service.

        Args:
            vector_service: Internal service used to perform vector database queries.
            client: Google genai client instance contains credentials and endpoint interaction.
            timeout: Request timeout applied when the service instantiates a client.
            default_top_k: Default number of results returned from the vector database.
        """

        if vector_service is None:
            msg = "A vector_service must be provided."
            raise ValueError(msg)

        if client is None:
            msg = "A google genai client must be provided."
            raise ValueError(msg)

        if default_top_k <= 0:
            msg = "default_top_k must be a positive integer."
            raise ValueError(msg)

        self._client = client
        self._timeout = timeout
        self._default_top_k = default_top_k
        self._vector_service = vector_service

    async def _post(
        self,
        client: genai.client.AsyncClient,
        payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Call google gen ai endpoint with client."""
        embeddings: list[list[float]] = []
        response = client.models.embed_content(
                    model='gemini-embedding-001',
                    contents=payload['text']
                )
        embeddings = embeddings + [e.values for e in response.embeddings]
        result = {"embeddings" : embeddings[0]}

        #try:
        #    data = response.json()
        #except ValueError as exc:
        #    logger.exception("RAG service returned invalid JSON: {}", exc)
        #    raise RagServiceError("External service returned invalid JSON.") from exc

        #if not isinstance(data, dict):
        #    msg = "External service response must be a JSON object."
        #    logger.error(msg)
        #    raise RagServiceError(msg)

        return result

    async def calculate_embedding(self, text: str) -> list[float]:
        """Generate an embedding for the supplied text using the external API."""

        payload = {"text": text}
        logger.debug("Requesting embedding for text of length {}", len(text))
        data = await self._post(self._client, payload)

        embedding = data['embeddings']
        if embedding is None:
            msg = "Embedding response is missing the 'embedding' field."
            logger.error(msg)
            raise RagServiceError(msg)

        if not isinstance(embedding, Sequence) or isinstance(embedding, (bytes, str)):
            msg = "Embedding must be returned as a sequence of numeric values."
            logger.error(msg)
            raise RagServiceError(msg)

        try:
            vector = [float(value) for value in embedding]
        except (TypeError, ValueError) as exc:
            logger.exception("Embedding values are not numeric: {}", exc)
            raise RagServiceError("Embedding contains non-numeric values.") from exc

        if not vector:
            msg = "Embedding vector may not be empty."
            logger.error(msg)
            raise RagServiceError(msg)

        return vector

    async def query_vector_database(
        self,
        embedding: Sequence[float],
        *,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query the vector database using the supplied embedding."""

        if not embedding:
            msg = "An embedding vector is required to query the database."
            logger.error(msg)
            raise RagServiceError(msg)

        limit = top_k or self._default_top_k
        if limit <= 0:
            msg = "top_k must be a positive integer."
            logger.error(msg)
            raise RagServiceError(msg)

        logger.debug("Querying vector database with top_k={}", limit)

        try:
            results = await self._vector_service.similarity_search(
                embedding, limit=limit
            )
        except Exception as exc:  # pragma: no cover - service specific errors
            logger.exception("Vector database query failed: {}", exc)
            raise RagServiceError("Vector database query failed.") from exc

        formatted_results = [
            {"id": item.id, "score": item.score, "payload": item.payload}
            for item in results
        ]

        return formatted_results

    async def run(self, text: str, *, top_k: int | None = None) -> list[dict[str, Any]]:
        """Execute the RAG pipeline: embed the text and query the vector database."""

        embedding = await self.calculate_embedding(text)
        return await self.query_vector_database(embedding, top_k=top_k)