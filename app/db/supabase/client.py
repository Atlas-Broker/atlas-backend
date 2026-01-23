"""Supabase PostgreSQL async client."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.db.supabase.models import Base
from loguru import logger

# Global engine and session maker
_engine = None
_async_session_maker = None


def get_engine():
    """Get or create SQLAlchemy async engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.ENVIRONMENT == "development",
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        logger.info("Created Supabase async engine")
    return _engine


def get_session_maker() -> async_sessionmaker:
    """Get or create async session maker."""
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info("Created Supabase session maker")
    return _async_session_maker


async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI to get database session.

    Yields:
        AsyncSession: Database session
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database connection (called on startup)."""
    engine = get_engine()
    logger.info("Supabase database initialized")
    # Note: Don't create tables here - use migrations instead


async def close_db():
    """Close database connection (called on shutdown)."""
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("Supabase database connection closed")
        _engine = None
