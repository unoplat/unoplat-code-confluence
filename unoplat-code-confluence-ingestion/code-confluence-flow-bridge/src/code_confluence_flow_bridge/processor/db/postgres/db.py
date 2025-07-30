# Standard library imports
import os
from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# Third-party imports
from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    async_sessionmaker, 
    async_scoped_session,
    create_async_engine,
    AsyncSessionTransaction
)
from sqlmodel import SQLModel

# PostgreSQL connection settings - read from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "code_confluence")

# Construct PostgreSQL connection string
POSTGRES_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create async engine - this can be shared across tasks/threads
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
async_engine = create_async_engine(
    POSTGRES_URL, 
    echo=DB_ECHO,
    pool_size=20,  # Increased pool size for concurrent workflows
    max_overflow=10
)

# Create AsyncSession factory (public name, no underscore prefix)
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine, 
    expire_on_commit=False,  # Critical for async to prevent implicit I/O
    class_=AsyncSession
)

# Create scoped session that provides per-task isolation
# This follows SQLAlchemy best practices for concurrent async operations
AsyncScopedSession = async_scoped_session(
    AsyncSessionFactory,
    scopefunc=current_task  # Each asyncio task gets its own session
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session using a context manager.
    
    This provides backward compatibility but uses the scoped session internally.
    Uses async_scoped_session to ensure each asyncio task (including Temporal
    workflows and activities) gets its own session instance, preventing
    concurrent access errors. Uses .begin() for proper transaction management.
    """
    try:
        session = AsyncScopedSession()
        async with session.begin():
            yield session
    except Exception as e:
        logger.error(f"Session error: {e}")
        raise
    finally:
        # Remove the session from the scope to prevent memory leaks
        await AsyncScopedSession.remove()


# Create alias for backwards compatibility
get_session_cm = asynccontextmanager(get_session)


async def create_db_and_tables() -> None:
    """Asynchronously create database tables and ensure the database engine is bound to the current event loop.

    During test execution (e.g. when FastAPI's TestClient spins up the application inside a
    new thread), the lifespan event handler is executed inside a *new* asyncio event loop.
    A SQLAlchemy ``AsyncEngine`` retains a reference to the loop in which it was created,
    therefore using a *module-level* engine across multiple event loops results in the
    classic

        RuntimeError: got Future <...> attached to a different loop

    error that we are seeing in CI.

    Strategy:
    1. Dispose the existing ``async_engine`` (if any) so that all associated connections
       are closed.
    2. Re-create a *fresh* engine bound to *this* event loop
    3. Rebuild the scoped session factory so that newly created sessions use the fresh
       engine.
    """
    global async_engine, AsyncScopedSession, AsyncSessionFactory  # we are going to re-assign these

    # Step 1 – dispose previously created engine (if the application is being
    # restarted inside the same interpreter, e.g. by TestClient between tests)
    try:
        await async_engine.dispose()
    except Exception:
        # The engine might not have been initialised yet – ignore.
        pass

    # Step 2 – create a brand-new engine bound to *this* event loop
    async_engine = create_async_engine(
        POSTGRES_URL, 
        echo=DB_ECHO,
        pool_size=20,
        max_overflow=10
    )

    # Step 3 – rebuild the session factory and scoped session so they point at the new engine
    AsyncSessionFactory = async_sessionmaker(
        bind=async_engine, 
        expire_on_commit=False,
        class_=AsyncSession
    )
    
    # Recreate the scoped session with the new factory
    AsyncScopedSession = async_scoped_session(
        AsyncSessionFactory,
        scopefunc=current_task
    )

    # Finally, create all tables if they are missing.
    async with async_engine.begin() as conn:
        try:
            await conn.run_sync(lambda sync_conn: SQLModel.metadata.create_all(sync_conn, checkfirst=True))
        except Exception as e:
            # Handle index already exists errors gracefully
            if "already exists" in str(e):
                logger.warning(f"Database schema creation encountered existing objects: {e}")
                # Continue execution - this is expected in test environments
            else:
                raise