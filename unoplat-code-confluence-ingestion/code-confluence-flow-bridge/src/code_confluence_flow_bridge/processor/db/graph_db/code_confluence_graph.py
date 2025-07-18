# Standard Library
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)

from loguru import logger

# Third Party
from neomodel import adb, config  # type: ignore
from .txn_context import managed_tx


class CodeConfluenceGraph:
    """
    Async Neo4j graph database connection manager using neomodel
    Implements singleton pattern to ensure single global connection
    """
    _instance = None
    _initialized = False

    def __new__(cls, code_confluence_env: EnvironmentSettings):
        """Singleton pattern: ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, code_confluence_env: EnvironmentSettings):
        """Initialize connection settings (only once due to singleton)"""
        if self._initialized:
            return
            
        host = code_confluence_env.neo4j_host
        port = code_confluence_env.neo4j_port
        username = code_confluence_env.neo4j_username
        password = code_confluence_env.neo4j_password.get_secret_value()
        max_connection_lifetime = code_confluence_env.neo4j_max_connection_lifetime
        max_connection_pool_size = code_confluence_env.neo4j_max_connection_pool_size
        connection_acquisition_timeout = code_confluence_env.neo4j_connection_acquisition_timeout

        if not all([host, port, username, password]):
            raise ValueError("Required environment variables NEO4J_HOST, NEO4J_PORT, NEO4J_USERNAME, NEO4J_PASSWORD must be set")

        self.connection_url = f"bolt://{username}:{password}@{host}:{port}" f"?max_connection_lifetime={max_connection_lifetime}" f"&max_connection_pool_size={max_connection_pool_size}" f"&connection_acquisition_timeout={connection_acquisition_timeout}"
        config.DATABASE_URL = self.connection_url
        self._initialized = True
        logger.info("Neo4j connection settings initialized")

    async def connect(self) -> None:
        """Establish async connection to Neo4j"""
        try:
            await adb.set_connection(self.connection_url)
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

    @property
    def transaction(self):
        """Return a *new* managed Neo4j transaction context manager.

        The returned object can be used directly in ``async with`` blocks:

        >>> async with graph.transaction:
        ...     ...
        """
        # Each call must create a *fresh* context-manager instance, hence the
        # trailing parenthesis.
        return managed_tx()
