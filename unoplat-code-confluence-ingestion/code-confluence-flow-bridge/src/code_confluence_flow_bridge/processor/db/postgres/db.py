# Standard library imports
import os
import asyncio
from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import HTTPException

# Third-party imports
from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase

# PostgreSQL connection settings - read from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "code_confluence")

# Construct PostgreSQL connection string
POSTGRES_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Database echo setting
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

# Global registry to store engines per event loop with thread-safe access
# This ensures each event loop gets its own AsyncEngine instance while sharing
# engines across all tasks ithin the same loop (fixing Temporal activity timeouts)
_engine_per_loop: dict[int, tuple[AsyncEngine, async_sessionmaker]] = {}
_engine_lock = asyncio.Lock()


async def get_engine_for_loop() -> tuple[AsyncEngine, async_sessionmaker]:
    """Get or create AsyncEngine for current event loop.

    This function ensures that each event loop has its own AsyncEngine instance,
    preventing "Future attached to a different loop" errors when running in
    multiple event loops (e.g., during testing). Uses a global registry with
    asyncio.Lock to ensure thread safety and engine sharing across tasks.

    Returns:
        Tuple of (engine, session_factory) for the current event loop
    """
    loop = asyncio.get_running_loop()
    loop_id = id(loop)

    log_ctx = logger.bind(loop_id=loop_id)
    log_ctx.debug("Attempting to retrieve AsyncEngine for loop {loop_id}")

    # Use lock to ensure thread-safe access to global registry
    async with _engine_lock:
        if loop_id not in _engine_per_loop:
            log_ctx.debug("No AsyncEngine found for loop {loop_id}, creating new instance")
            # Create new engine for this loop
            engine = create_async_engine(
                POSTGRES_URL,
                echo=DB_ECHO,
                pool_size=20,  # Increased pool size for concurrent workflows
                max_overflow=10,
            )

            # Create session factory for this engine
            session_factory = async_sessionmaker(
                bind=engine,
                expire_on_commit=False,  # Critical for async to prevent implicit I/O
                class_=AsyncSession,
            )

            # Store in global registry
            _engine_per_loop[loop_id] = (engine, session_factory)

            log_ctx.success("Created new AsyncEngine and session factory for loop {loop_id}")
        else:
            log_ctx.debug("Reusing cached AsyncEngine for loop {loop_id}")

    return _engine_per_loop[loop_id]


# ---------------------------------------------------------------------------
# Session management helper
# ---------------------------------------------------------------------------

async def get_session() -> AsyncGenerator[async_scoped_session, None]:
    """Yield a database session using the engine for current event loop.

    This function ensures that database sessions use the correct AsyncEngine
    for the current event loop, preventing cross-loop Future errors.
    Uses async_scoped_session to ensure each asyncio task gets its own
    session instance with proper transaction management.
    """
    # Build a bound logger containing contextual information useful for
    # troubleshooting concurrent executions.
    loop_id = id(asyncio.get_running_loop())
    task = current_task()
    task_name = task.get_name() if task else "unknown"
    log_ctx = logger.bind(loop_id=loop_id, task=task_name)

    log_ctx.debug("Creating new DB session (task={task}, loop_id={loop_id})")

    scoped_session: async_scoped_session | None = None
    try:
        # Get engine and session factory for current loop
        _, session_factory = await get_engine_for_loop()

        # Create scoped session for this engine
        scoped_session = async_scoped_session(
            session_factory,
            scopefunc=current_task,
        )

        log_ctx.debug("Scoped session created; beginning transactional context")

        async with scoped_session.begin():
            log_ctx.debug("Session transaction started")
            yield scoped_session
            log_ctx.debug(
                "Session transaction finished, changes will be committed on context exit"
            )
    except HTTPException:
        # Let FastAPI handle expected HTTP errors without logging as server errors
        raise
    except Exception as exc:
        # Use .exception() to include the full traceback according to Loguru docs.
        log_ctx.exception("Unexpected error inside DB session context: {}", exc)
        raise
    finally:
        if scoped_session is not None:
            try:
                await scoped_session.remove()
                log_ctx.debug("Scoped session removed from registry (session cleanup complete)")
            except Exception as cleanup_exc:
                log_ctx.warning("Failed to clean up scoped session: {}", cleanup_exc)


# Create alias for backwards compatibility
get_session_cm = asynccontextmanager(get_session)


async def create_db_and_tables() -> None:
    """Create database tables using the engine for current event loop.

    This function now works with the per-loop engine pattern, ensuring
    that database schema creation uses the correct engine for the current
    event loop. This prevents "Future attached to a different loop" errors
    during testing or when running in multiple event loops.
    """
    # Get engine for current loop
    engine, _ = await get_engine_for_loop()

    # Create all tables if they are missing
    async with engine.begin() as conn:
        try:
            await conn.run_sync(lambda sync_conn: SQLBase.metadata.create_all(sync_conn, checkfirst=True))
            logger.success("Database tables created successfully")
        except Exception as e:
            # Handle index already exists errors gracefully
            if "already exists" in str(e):
                logger.warning("Database schema creation encountered existing objects: {}", e)
                # Continue execution - this is expected in test environments
            else:
                raise


async def dispose_current_engine() -> None:
    """Dispose the engine for the current event loop.

    This is useful for cleanup operations, especially during application shutdown.
    """
    loop = asyncio.get_running_loop()
    loop_id = id(loop)

    async with _engine_lock:
        if loop_id in _engine_per_loop:
            try:
                engine, _ = _engine_per_loop[loop_id]
                await engine.dispose()
                logger.success("Disposed AsyncEngine for current event loop {}", loop_id)

                # Remove from registry
                del _engine_per_loop[loop_id]
            except Exception as e:
                logger.warning("Failed to dispose engine for current loop {}: {}", loop_id, e)
        else:
            logger.debug("No engine found for current loop to dispose")
