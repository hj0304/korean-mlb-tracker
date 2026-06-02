"""FastAPI dependencies (dependency injection)."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped async DB session."""
    async with get_session_maker()() as session:
        yield session
