from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Optional

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings

# Global variables for async engine and session management
async_engine: Optional[AsyncEngine] = None
AsyncSessionFactory: Optional[async_sessionmaker[AsyncSession]] = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session per HTTP request.

    Yields a fresh AsyncSession for each request with automatic transaction management.
    The session is created from AsyncSessionFactory (not async_scoped_session).
    Each request gets its own isolated session instance.

    Yields:
        AsyncSession: Database session for the request

    Raises:
        RuntimeError: If database connections are not initialized
    """
    if AsyncSessionFactory is None:
        raise RuntimeError(
            "Database connections not initialized. Call init_db_connections() first."
        )

    session = AsyncSessionFactory()
    try:
        async with session.begin():
            yield session
    except Exception as e:
        logger.error("Session error: {}", e)
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_startup_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for non-request contexts (startup, background tasks).

    This context manager is used for operations outside of HTTP request lifecycle,
    such as application startup, shutdown, and background tasks.

    Yields:
        AsyncSession: Database session with automatic transaction management

    Raises:
        RuntimeError: If database connections are not initialized
    """
    if AsyncSessionFactory is None:
        raise RuntimeError(
            "Database connections not initialized. Call init_db_connections() first."
        )

    session = AsyncSessionFactory()
    try:
        async with session.begin():
            yield session
    except Exception as e:
        logger.error("Session error: {}", e)
        raise
    finally:
        await session.close()


async def init_db_connections(settings: EnvironmentSettings) -> None:
    """Initialize database connections using settings and ensure the engine is bound to the current event loop.

    This function handles multi-event loop scenarios (like in tests) by:
    1. Disposing the existing engine (if any) to close all connections
    2. Creating a fresh engine bound to the current event loop
    3. Creating a session factory for request-scoped sessions

    Args:
        settings: Environment settings containing database configuration

    Note: This function does NOT create database tables. Table creation is the
    responsibility of the ingestion project.
    """
    global async_engine, AsyncSessionFactory

    try:
        if async_engine is not None:
            await async_engine.dispose()
    except Exception:
        pass

    async_engine = create_async_engine(
        settings.postgres_url, echo=settings.db_echo, pool_size=20, max_overflow=10
    )

    AsyncSessionFactory = async_sessionmaker(
        bind=async_engine, expire_on_commit=False, class_=AsyncSession
    )

    logger.info("Database connections initialized successfully")


async def dispose_db_connections() -> None:
    """Dispose database connections and clean up resources."""
    global async_engine
    try:
        if async_engine is not None:
            await async_engine.dispose()
        logger.info("Database connections disposed successfully")
    except Exception as e:
        logger.error("Error disposing database connections: {}", e)
