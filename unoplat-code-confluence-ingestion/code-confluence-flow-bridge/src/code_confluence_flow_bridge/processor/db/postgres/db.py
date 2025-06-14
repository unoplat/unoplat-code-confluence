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
    """Asynchronously create database tables."""
    async with async_engine.begin() as conn:
        # Use create_all with checkfirst=True to avoid errors if tables already exist
        await conn.run_sync(lambda sync_conn: SQLModel.metadata.create_all(sync_conn, checkfirst=True))