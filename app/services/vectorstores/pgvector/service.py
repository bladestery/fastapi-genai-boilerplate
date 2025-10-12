"""Service layer orchestrating PGVector repository operations."""

from __future__ import annotations

from collections.abc import Sequence

from loguru import logger

from app.services.vectorstores.interfaces import VectorSearchResult, VectorStoreService

from .repository import PgVectorRepository


class PgVectorService(VectorStoreService):
    """Application service exposing PGVector search capabilities."""

    def __init__(self, repository: PgVectorRepository) -> None:
        self._repository = repository

    async def similarity_search(
        self, embedding: Sequence[float], *, limit: int
    ) -> list[VectorSearchResult]:
        if limit <= 0:
            msg = "limit must be greater than zero"
            logger.error(msg)
            raise ValueError(msg)

        rows = await self._repository.similarity_search(embedding, limit=limit)

        results: list[VectorSearchResult] = []
        for document, score in rows:
            payload = {
                "content": document.description,
            }
            results.append(
                VectorSearchResult(
                    id=str(document.id),
                    score=score,
                    payload=payload,
                )
            )

        return results


__all__ = ["PgVectorService"]