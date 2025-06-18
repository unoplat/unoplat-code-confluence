import os
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

# PostgreSQL connection settings - read from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "code_confluence")

# Construct PostgreSQL connection string
POSTGRES_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create async engine
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
async_engine = create_async_engine(POSTGRES_URL, echo=DB_ECHO)

# Create AsyncSession factory
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def get_session():
    """Yield a database session using a context manager."""
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_session_cm():
    """Async context manager for database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_and_tables():
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
    3. Rebuild the ``AsyncSession`` factory so that newly created sessions use the fresh
       engine.
    """
    global async_engine, AsyncSessionLocal  # we are going to re-assign these

    # Step 1 – dispose previously created engine (if the application is being
    # restarted inside the same interpreter, e.g. by TestClient between tests)
    try:
        await async_engine.dispose()
    except Exception:
        # The engine might not have been initialised yet – ignore.
        pass

    # Step 2 – create a brand-new engine bound to *this* event loop
    async_engine = create_async_engine(POSTGRES_URL, echo=DB_ECHO)

    # Step 3 – rebuild the session factory so it points at the new engine
    AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)

    # Finally, create all tables if they are missing.
    async with async_engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: SQLModel.metadata.create_all(sync_conn, checkfirst=True))