"""
Synchronous database utilities for testing.

This module provides utilities for creating synchronous database sessions
for testing purposes, avoiding async event loop conflicts while maintaining
proper transaction isolation.
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
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