from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Optional

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings

# Global variables for async engine and session management
async_engine: Optional[AsyncEngine] = None
AsyncSessionFactory: Optional[async_sessionmaker[AsyncSession]] = None
AsyncScopedSession: Optional[async_scoped_session[AsyncSession]] = None


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session using a context manager.

    Uses async_scoped_session to ensure each asyncio task gets its own
    session instance, preventing concurrent access errors across different
    tools and concurrent agents.
    """
    if AsyncScopedSession is None:
        raise RuntimeError(
            "Database connections not initialized. Call init_db_connections() first."
        )

    try:
        # Obtain a task-scoped AsyncSession and yield it
        session = AsyncScopedSession()
        async with session.begin():
            yield session
    except Exception as e:
        logger.error("Session error: Error: {}", e)
        raise
    finally:
        # Ensure the scoped session is removed for this task
        await AsyncScopedSession.remove()


async def init_db_connections(settings: EnvironmentSettings) -> None:
    """Initialize database connections using settings and ensure the engine is bound to the current event loop.

    This function handles multi-event loop scenarios (like in tests) by:
    1. Disposing the existing engine (if any) to close all connections
    2. Creating a fresh engine bound to the current event loop
    3. Rebuilding the scoped session factory with the new engine

    Args:
        settings: Environment settings containing database configuration

    Note: This function does NOT create database tables. Table creation is the
    responsibility of the ingestion project.
    """
    global async_engine, AsyncSessionFactory, AsyncScopedSession
    
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

    AsyncScopedSession = async_scoped_session(
        AsyncSessionFactory, scopefunc=current_task
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
