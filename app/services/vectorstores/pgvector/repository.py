"""Data access layer for the PGVector store."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Iterable

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .models import PgVectorDocument


class PgVectorRepository:
    """Repository handling read operations against the PGVector table."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    def _build_similarity_query(
        self, embedding: Sequence[float], *, limit: int
    ) -> Select[tuple[PgVectorDocument, float]]:
        """Prepare the similarity search query."""

        distance = PgVectorDocument.embedding.cosine_distance(list(embedding))
        return (
            select(PgVectorDocument, distance.label("score"))
            .order_by(distance)
            .limit(limit)
        )

    async def similarity_search(
        self, embedding: Sequence[float], *, limit: int
    ) -> list[tuple[PgVectorDocument, float]]:
        """Fetch the closest documents to the given embedding."""

        stmt = self._build_similarity_query(embedding, limit=limit)

        async with self._session_factory() as session:
            result = await session.execute(stmt)
            records = result.all()

        rows: Iterable[tuple[PgVectorDocument, float]] = (
            (document, float(score)) for document, score in records
        )
        return list(rows)


__all__ = ["PgVectorRepository"]