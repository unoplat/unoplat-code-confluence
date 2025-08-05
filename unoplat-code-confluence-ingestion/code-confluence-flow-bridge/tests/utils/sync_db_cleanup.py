"""
Synchronous database cleanup utilities for test isolation.

These utilities provide simple synchronous functions to clear data from
Neo4j and PostgreSQL databases during tests.
"""

from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session


def cleanup_neo4j_sync(db) -> None:
    """
    Clear all data from Neo4j database.

    Args:
        db: neomodel db object from neo4j_client fixture
    """
    try:
        db.cypher_query("MATCH (n) DETACH DELETE n")
        logger.debug("Neo4j database cleared successfully")
    except Exception as e:
        logger.error(f"Failed to cleanup Neo4j: {e}")
        raise


def cleanup_postgresql_sync(session: Session) -> None:
    """
    Clear all data from PostgreSQL repository table.

    Deletes from repository table only - CASCADE constraints will handle related tables:
    - codebase_config
    - repository_workflow_run
    - codebase_workflow_run

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
        session.rollback()
        logger.error(f"Failed to cleanup PostgreSQL: {e}")
        raise
