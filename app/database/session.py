"""Session management for the application's database layer."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(settings.PG_URL, echo=False, future=True)

async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Provide a transactional scope around a series of operations."""

    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:  # pragma: no cover - defensive rollback
        await session.rollback()
        raise
    finally:
        await session.close()


__all__ = ["engine", "async_session_factory", "get_session"]