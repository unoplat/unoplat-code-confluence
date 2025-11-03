"""
Synchronous database utilities for testing.

This module provides utilities for creating synchronous database sessions
for testing purposes, avoiding async event loop conflicts while maintaining
proper transaction isolation.
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool


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