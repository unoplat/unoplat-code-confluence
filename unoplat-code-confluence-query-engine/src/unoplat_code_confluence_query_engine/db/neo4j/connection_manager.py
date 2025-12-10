from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger
from neo4j import AsyncDriver, AsyncSession
from neomodel import adb, config  # type: ignore

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings


class CodeConfluenceGraphQueryEngine:
    """
    Async Neo4j graph database connection manager using neomodel for the Query Engine.

    Provides managed transaction support for read operations and query execution.
    Similar to the ingestion project's CodeConfluenceGraph but focused on read operations.
    Does not handle schema creation as that is managed by the ingestion component.
    """

    def __init__(self, settings: EnvironmentSettings):
        """Initialize connection settings from environment configuration."""

        self.connection_url = settings.neo4j_url
        config.DATABASE_URL = self.connection_url
        logger.info("Neo4j connection settings initialized for query engine")
        self.adb_driver: AsyncDriver

    async def connect(self) -> None:
        """Establish async connection to Neo4j using neomodel's adb."""
        try:
            await adb.set_connection(self.connection_url)
            self.adb_driver = adb.driver
            logger.info("Successfully connected to Neo4j database for query engine")
        except Exception as e:
            logger.error("Failed to connect to Neo4j: {}", str(e))
            raise

    async def close(self) -> None:
        """Close the async connection."""
        try:
            await adb.close_connection()
            logger.info("Successfully closed Neo4j connection")
        except Exception as e:
            logger.error(f"Error closing Neo4j connection: {e!s}")
            raise

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an async session from the connection pool.

        Query engine activities should use session.execute_read() for read operations
        and session.execute_write() for any write operations with automatic retry.

        Yields:
            AsyncSession: A Neo4j session from the connection pool
        """
        async with self.adb_driver.session() as session:
            yield session
