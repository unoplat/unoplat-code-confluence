# Standard Library
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from neo4j import AsyncDriver, AsyncSession
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)


from loguru import logger

# Third Party
from neomodel import adb, config  # type: ignore


class CodeConfluenceGraph:
    """
    Async Neo4j graph database connection manager using neomodel
    Provides managed transaction support for concurrent activities
    """

    def __init__(self, code_confluence_env: EnvironmentSettings):
        """Initialize connection settings"""

        host = code_confluence_env.neo4j_host
        port = code_confluence_env.neo4j_port
        username = code_confluence_env.neo4j_username
        password = code_confluence_env.neo4j_password.get_secret_value()
        max_connection_lifetime = code_confluence_env.neo4j_max_connection_lifetime
        max_connection_pool_size = code_confluence_env.neo4j_max_connection_pool_size
        connection_acquisition_timeout = (
            code_confluence_env.neo4j_connection_acquisition_timeout
        )

        if not all([host, port, username, password]):
            raise ValueError(
                "Required environment variables NEO4J_HOST, NEO4J_PORT, NEO4J_USERNAME, NEO4J_PASSWORD must be set"
            )

        self.connection_url = (
            f"bolt://{username}:{password}@{host}:{port}"
            f"?max_connection_lifetime={max_connection_lifetime}"
            f"&max_connection_pool_size={max_connection_pool_size}"
            f"&connection_acquisition_timeout={connection_acquisition_timeout}"
        )
        config.DATABASE_URL = self.connection_url
        logger.info("Neo4j connection settings initialized")
        self.adb_driver: AsyncDriver

    async def connect(self) -> None:
        """Establish async connection to Neo4j"""
        try:
            await adb.set_connection(self.connection_url)
            self.adb_driver = adb.driver
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise

    async def close(self) -> None:
        """Close the async connection"""
        try:
            await adb.close_connection()
            logger.info("Successfully closed Neo4j connection")
        except Exception as e:
            logger.error(f"Error closing Neo4j connection: {str(e)}")
            raise

    async def create_schema(self) -> None:
        """Create schema asynchronously"""
        try:
            await adb.install_all_labels()
            logger.info("Successfully installed all labels")
        except Exception as e:
            logger.error(f"Failed to create schema: {str(e)}")
            raise

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an async session from the connection pool.
        Activities should use session.execute_write() and session.execute_read()
        for managed transactions with automatic retry.

        Yields:
            AsyncSession: A Neo4j session from the connection pool
        """
        async with self.adb_driver.session() as session:
            yield session
