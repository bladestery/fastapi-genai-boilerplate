"""Shared interfaces for vector store services."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class VectorSearchResult:
    """Represents a single vector similarity match."""

    id: str
    score: float
    payload: dict[str, Any]


class VectorStoreService(Protocol):
    """Abstract service definition for vector database operations."""

    async def similarity_search(
        self, embedding: Sequence[float], *, limit: int
    ) -> list[VectorSearchResult]:
        """Return the closest matches for an embedding."""


__all__ = ["VectorSearchResult", "VectorStoreService"]