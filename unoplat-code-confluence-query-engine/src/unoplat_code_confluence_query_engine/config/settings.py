from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Compute absolute path to .env.dev from settings.py location
# settings.py is at: src/unoplat_code_confluence_query_engine/config/settings.py
# .env.dev is at: project root (unoplat-code-confluence-query-engine/.env.dev)
_ENV_FILE_PATH = Path(__file__).parent.parent.parent.parent / ".env.dev"


class EnvironmentSettings(BaseSettings):
    """
    Environment settings for the Unoplat Code Confluence Query Engine.

    Loads configuration from environment variables with proper typing and validation.
    Uses Pydantic Settings for secure handling of sensitive data.
    """

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
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
        description="32-byte Fernet encryption key for credentials (must match ingestion project)",
    )

    # Logging Settings
    log_level: str = Field(default="DEBUG", alias="LOG_LEVEL")
    log_rotation_size: str = Field(default="10 MB", alias="LOG_ROTATION_SIZE")
    log_retention_days: int = Field(default=30, alias="LOG_RETENTION_DAYS")

    # LOGFIRE TELEMETRY
    logfire_sdk_write_key: Optional[SecretStr] = Field(
        default=None,
        alias="LOGFIRE_SDK_WRITE_KEY",
        description="Logfire SDK write key for logging",
        validate_default=False,
    )

    # HTTP Retry Settings
    retry_enabled: bool = Field(
        default=False,
        alias="HTTP_RETRY_ENABLED",
        description="Enable HTTP retry logic for AI model providers",
    )
    retry_max_attempts: int = Field(
        default=3,
        alias="HTTP_RETRY_MAX_ATTEMPTS",
        description="Maximum number of retry attempts",
        ge=1,
        le=10,
    )
    retry_base_wait: float = Field(
        default=1.0,
        alias="HTTP_RETRY_BASE_WAIT",
        description="Base wait time in seconds for exponential backoff",
        ge=0.1,
        le=10.0,
    )
    retry_max_wait: int = Field(
        default=60,
        alias="HTTP_RETRY_MAX_WAIT",
        description="Maximum wait time in seconds between retries",
        ge=1,
        le=300,
    )
    retry_timeout: float = Field(
        default=30.0,
        alias="HTTP_RETRY_TIMEOUT",
        description="HTTP request timeout in seconds",
        ge=5.0,
        le=300.0,
    )
    retry_status_codes: str = Field(
        default="429,502,503,504",
        alias="HTTP_RETRY_STATUS_CODES",
        description="Comma-separated list of HTTP status codes to retry",
    )

    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Mock SSE Settings
    mock_sse_enabled: bool = Field(
        default=False,
        alias="MOCK_SSE_ENABLED",
        description="Enable mock SSE mode for testing without running actual agents",
    )
    mock_sse_delay_seconds: float = Field(
        default=0.5,
        alias="MOCK_SSE_DELAY_SECONDS",
        description="Artificial delay between mock SSE events",
        ge=0.0,
        le=2.0,
    )
    mock_sse_log_path: str = Field(
        default="/Users/jayghiya/Documents/unoplat/unoplat-code-confluence/unoplat-code-confluence-query-engine/docs/mock/database-agent-events.json",
        alias="MOCK_SSE_LOG_PATH",
        description="Path to mock workflow events JSON",
    )

    mock_sse_result_path: str = Field(
        default="/Users/jayghiya/Documents/unoplat/unoplat-code-confluence/unoplat-code-confluence-query-engine/docs/mock/agent-md-result.json",
        alias="MOCK_SSE_RESULT_PATH",
        description="Path to mock final agent MD result JSON",
    )

    # Temporal Settings
    temporal_address: str = Field(
        default="localhost:7233",
        alias="TEMPORAL_ADDRESS",
        description="Temporal server address for workflows",
    )
    temporal_namespace: str = Field(
        default="default",
        alias="TEMPORAL_NAMESPACE",
        description="Temporal namespace for workflows",
    )
    temporal_enabled: bool = Field(
        default=True,
        alias="TEMPORAL_ENABLED",
        description="Enable Temporal worker at app startup",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def retry_status_codes_list(self) -> list[int]:
        """Parse retry status codes string into list of integers."""
        return [int(code.strip()) for code in self.retry_status_codes.split(",")]

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
