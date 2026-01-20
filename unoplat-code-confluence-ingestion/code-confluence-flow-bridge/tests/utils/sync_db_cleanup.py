"""
Synchronous database cleanup utilities for test isolation.

These utilities provide simple synchronous functions to clear data from
PostgreSQL databases during tests.
"""

from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session


def cleanup_postgresql_sync(session: Session) -> None:
    """
    Clear all data from PostgreSQL repository and Code Confluence relational tables.

    Deletes from repository table only - CASCADE constraints will handle related tables:
    - codebase_config
    - repository_workflow_run
    - codebase_workflow_run

    Also truncates Code Confluence relational ingestion tables:
    - code_confluence_git_repository (CASCADE handles codebases, files, metadata, link tables)

    Args:
        session: SQLAlchemy synchronous session from get_sync_postgres_session context manager
    """
    try:
        # Fast truncate to remove all rows; CASCADE wipes dependent tables in one shot
        session.execute(text("TRUNCATE TABLE repository CASCADE"))
        session.execute(text("TRUNCATE TABLE code_confluence_git_repository CASCADE"))
        session.commit()
        session.flush()
        logger.debug("PostgreSQL repository data cleared successfully")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to cleanup PostgreSQL: {e}")
        raise
