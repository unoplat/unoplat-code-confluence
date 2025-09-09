from typing import Optional
from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentSettings(BaseSettings):
    """
    Environment settings for the Unoplat Code Confluence Query Engine.

    Loads configuration from environment variables with proper typing and validation.
    Uses Pydantic Settings for secure handling of sensitive data.
    """

    model_config = SettingsConfigDict(
        env_file="../../.env.dev",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_default=True,
        extra="ignore"
    )

    # PostgreSQL Database Settings
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: SecretStr = Field(default=SecretStr("postgres"), alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="code_confluence", alias="DB_NAME")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # Neo4j Database Settings
    neo4j_host: str = Field(default="localhost", alias="NEO4J_HOST")
    neo4j_port: int = Field(default=7687, alias="NEO4J_PORT")
    neo4j_username: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: SecretStr = Field(
        default=SecretStr("password"), alias="NEO4J_PASSWORD"
    )
    neo4j_max_connection_lifetime: int = Field(
        default=3600, alias="NEO4J_MAX_CONNECTION_LIFETIME"
    )
    neo4j_max_connection_pool_size: int = Field(
        default=100, alias="NEO4J_MAX_CONNECTION_POOL_SIZE"
    )
    neo4j_connection_acquisition_timeout: int = Field(
        default=60, alias="NEO4J_CONNECTION_ACQUISITION_TIMEOUT"
    )

    # MCP Server Settings
    mcp_servers_enabled: bool = Field(default=True, alias="MCP_SERVERS_ENABLED")
    mcp_servers_config_path: str = Field(
        default="mcp-servers.json", alias="MCP_SERVERS_CONFIG_PATH"
    )
    
    # Encryption Settings
    token_encryption_key: SecretStr = Field(
        default=SecretStr("your-32-byte-fernet-key-here-replace-in-prod"),
        alias="TOKEN_ENCRYPTION_KEY",
        description="32-byte Fernet encryption key for credentials (must match ingestion project)"
    )
    
    # Logging Settings
    log_level: str = Field(default="DEBUG", alias="LOG_LEVEL")
    log_rotation_size: str = Field(default="10 MB", alias="LOG_ROTATION_SIZE")
    log_retention_days: int = Field(default=30, alias="LOG_RETENTION_DAYS")
    
    #LOGFIRE TELEMETRY
    logfire_sdk_write_key: Optional[SecretStr] = Field(
        default=None,
        alias="LOGFIRE_SDK_WRITE_KEY",
        description="Logfire SDK write key for logging",
        validate_default=False
    )
    
    environment: str = Field(default="development", alias="ENVIRONMENT")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def postgres_url(self) -> str:
        """Build PostgreSQL connection URL from settings."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def neo4j_url(self) -> str:
        """Build Neo4j Bolt connection URL from settings."""
        return (
            f"bolt://{self.neo4j_username}:{self.neo4j_password.get_secret_value()}"
            f"@{self.neo4j_host}:{self.neo4j_port}"
            f"?max_connection_lifetime={self.neo4j_max_connection_lifetime}"
            f"&max_connection_pool_size={self.neo4j_max_connection_pool_size}"
            f"&connection_acquisition_timeout={self.neo4j_connection_acquisition_timeout}"
        )
