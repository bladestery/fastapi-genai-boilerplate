"""SQLAlchemy models for the PGVector vector store."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.database import Base


class PgVectorDocument(Base):
    """Model representing a single document stored in PGVector."""

    __tablename__ = settings.VECTOR_TABLE_NAME

    id: Mapped[int] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=int
    )
    description: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(), nullable=False)


__all__ = ["PgVectorDocument"]