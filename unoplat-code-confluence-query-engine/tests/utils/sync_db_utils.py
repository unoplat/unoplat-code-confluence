"""
Synchronous database utilities for testing.

This module provides utilities for creating synchronous database sessions
for testing purposes, avoiding async event loop conflicts while maintaining
proper transaction isolation.
"""

from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from loguru import logger
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase


def create_sync_engine(db_url: str):
    """
    Create synchronous engine with NullPool for testing.

    Args:
        db_url: Database connection URL

    Returns:
        SQLAlchemy Engine configured for testing
    """
    return create_engine(
        db_url,
        poolclass=NullPool,  # Disable connection pooling for tests
        echo=False
    )


@contextmanager
def get_sync_postgres_session(port: int):
    """Yield a standalone Session tied to its own engine.

    A fresh engine and connection are created for each invocation, ensuring
    that no long-running transaction or lock is kept beyond the scope of the
    *with* block.  This avoids the ACCESS EXCLUSIVE lock problem we saw when
    `TRUNCATE … CASCADE` is executed inside a session that stays open for the
    whole test.

    Args:
        port: The host port on which the test Postgres instance is listening.
    """
    db_url = (
        f"postgresql+psycopg2://postgres:postgres@localhost:{port}/code_confluence"
    )
    engine = create_sync_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()


def cleanup_postgresql_sync(session: Session) -> None:
    """
    Clear all data from PostgreSQL repository table.

    Deletes from repository table only - CASCADE constraints will handle related tables:
    - codebase_config
    - repository_workflow_run
    - codebase_workflow_run
    - repository_agent_md_snapshot

    Args:
        session: SQLAlchemy synchronous session from get_sync_postgres_session context manager
    """
    try:
        # Fast truncate to remove all rows; CASCADE wipes dependent tables in one shot
        session.execute(text("TRUNCATE TABLE repository CASCADE"))
        session.commit()
        session.flush()
        logger.debug("PostgreSQL repository data cleared successfully")
    except Exception as e:
        # If tables don't exist yet, that's fine for tests
        if "does not exist" in str(e):
            logger.debug("PostgreSQL tables don't exist yet, skipping cleanup")
            session.rollback()
            return
        session.rollback()
        logger.error(f"Failed to cleanup PostgreSQL: {e}")
        raise


def create_test_tables(port: int) -> None:
    """Create database tables for testing using SQLModel metadata."""
    db_url = (
        f"postgresql+psycopg2://postgres:postgres@localhost:{port}/code_confluence"
    )
    engine = create_sync_engine(db_url)

    try:
        # Drop all existing tables to ensure fresh schema
        SQLBase.metadata.drop_all(engine)
        logger.debug("Dropped existing test database tables")

        # Create all tables defined in SQLBase metadata
        SQLBase.metadata.create_all(engine)
        logger.debug("Created test database tables successfully")
    except Exception as e:
        logger.error(f"Failed to create test tables: {e}")
        raise
    finally:
        engine.dispose()


@contextmanager
def sync_session_scope(engine):
    """
    Provide a transactional scope with proper cleanup.

    This context manager creates a session with savepoint isolation,
    ensuring that each test runs in its own transaction that can be
    rolled back for proper cleanup.

    Args:
        engine: SQLAlchemy engine

    Yields:
        Session: SQLAlchemy session with savepoint isolation
    """
    connection = engine.connect()
    trans = connection.begin()

    # Create session with create_savepoint mode for test isolation
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint"
    )

    try:
        yield session
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        session.close()
        connection.close()
