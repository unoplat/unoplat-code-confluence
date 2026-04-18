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

    # Codex OAuth Settings (ChatGPT subscription flow)
    codex_openai_client_id: str = Field(
        default="app_EMoamEEZ73f0CkXaXp7hrann",
        alias="CODEX_OPENAI_CLIENT_ID",
        description="OAuth client_id used for Codex ChatGPT flow",
    )
    codex_openai_issuer: str = Field(
        default="https://auth.openai.com",
        alias="CODEX_OPENAI_ISSUER",
        description="OpenAI OAuth issuer base URL",
    )
    codex_openai_originator: str = Field(
        default="opencode",
        alias="CODEX_OPENAI_ORIGINATOR",
        description="Originator query parameter for OAuth authorize URL",
    )
    codex_openai_api_endpoint: str = Field(
        default="https://chatgpt.com/backend-api/codex/responses",
        alias="CODEX_OPENAI_API_ENDPOINT",
        description="Codex backend endpoint receiving rewritten chat/responses calls",
    )
    codex_openai_callback_port: int = Field(
        default=1455,
        alias="CODEX_OPENAI_CALLBACK_PORT",
        description="Port for local Codex OAuth callback listener",
        ge=1,
        le=65535,
    )
    codex_openai_callback_hosts: str = Field(
        default="127.0.0.1,::1",
        alias="CODEX_OPENAI_CALLBACK_HOSTS",
        description=(
            "Comma-separated host addresses to bind for Codex OAuth callback listener "
            "(use 0.0.0.0 when running in Docker with published ports)"
        ),
    )
    codex_openai_redirect_uri: str = Field(
        default="http://localhost:1455/auth/callback",
        alias="CODEX_OPENAI_REDIRECT_URI",
        description="Exact redirect_uri used for Codex OAuth authorization code flow",
    )
    codex_openai_flow_ttl_seconds: int = Field(
        default=300,
        alias="CODEX_OPENAI_FLOW_TTL_SECONDS",
        description="OAuth flow expiration TTL in seconds",
        ge=60,
        le=1800,
    )
    codex_openai_poll_interval_ms: int = Field(
        default=1200,
        alias="CODEX_OPENAI_POLL_INTERVAL_MS",
        description="Suggested flow status polling interval in milliseconds",
        ge=250,
        le=10000,
    )
    codex_openai_token_refresh_safety_margin_seconds: int = Field(
        default=30,
        alias="CODEX_OPENAI_TOKEN_REFRESH_SAFETY_MARGIN_SECONDS",
        description="Refresh access token this many seconds before expiry",
        ge=0,
        le=300,
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

    # Development Workflow Docker Sandbox Settings
    dev_workflow_network_mode: str = Field(
        default="bridge",
        alias="DEV_WORKFLOW_NETWORK_MODE",
        description=(
            "Docker network mode for development workflow sandboxes "
            '("bridge", "none", "host", or "container:<name|id>"). '
            "Defaults to bridge so sandboxes can install packages and verify build commands."
        ),
    )
    dev_workflow_idle_timeout_seconds: int = Field(
        default=3600,
        alias="DEV_WORKFLOW_IDLE_TIMEOUT_SECONDS",
        description="Idle timeout in seconds for ephemeral Docker sandbox cleanup",
        ge=60,
        le=86400,
    )
    dev_workflow_python_image: str = Field(
        default=(
            "ghcr.io/unoplat/unoplat-code-confluence/"
            "code-confluence-dev-workflow-python:0.1.0"
        ),
        alias="DEV_WORKFLOW_PYTHON_IMAGE",
        description=(
            "Prebuilt Docker image used for Python development workflow sandboxes. "
            "Defaults to the repo-scoped GHCR package for unoplat/unoplat-code-confluence; "
            "override the tag or digest via environment when needed."
        ),
    )
    dev_workflow_typescript_image: str = Field(
        default=(
            "ghcr.io/unoplat/unoplat-code-confluence/"
            "code-confluence-dev-workflow-typescript:0.1.0"
        ),
        alias="DEV_WORKFLOW_TYPESCRIPT_IMAGE",
        description=(
            "Prebuilt Docker image used for TypeScript/JavaScript development workflow sandboxes. "
            "Defaults to the repo-scoped GHCR package for unoplat/unoplat-code-confluence; "
            "override the tag or digest via environment when needed."
        ),
    )

    # Agent Selection
    enabled_agents: str = Field(
        default="",
        alias="ENABLED_AGENTS",
        description=(
            "Comma-separated list of agent types to enable. "
            "Valid values: development_workflow_guide, dependency_guide, "
            "business_domain_guide, agents_md_updater, call_expression_validator. "
            "Empty string means all agents are enabled."
        ),
    )

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

    # Temporal Activity Retry Settings (for TemporalAgent activities)
    # Model activities - for LLM provider requests (more tolerant of transient issues)
    temporal_model_activity_max_attempts: int = Field(
        default=5,
        alias="TEMPORAL_MODEL_ACTIVITY_MAX_ATTEMPTS",
        description="Maximum retry attempts for model request activities",
        ge=1,
        le=10,
    )
    temporal_model_activity_initial_interval_s: float = Field(
        default=2.0,
        alias="TEMPORAL_MODEL_ACTIVITY_INITIAL_INTERVAL_S",
        description="Initial backoff interval in seconds for model activities",
        ge=0.5,
        le=30.0,
    )
    temporal_model_activity_backoff_coefficient: float = Field(
        default=2.0,
        alias="TEMPORAL_MODEL_ACTIVITY_BACKOFF_COEFFICIENT",
        description="Backoff coefficient for model activities",
        ge=1.0,
        le=5.0,
    )
    temporal_model_activity_max_interval_s: float = Field(
        default=60.0,
        alias="TEMPORAL_MODEL_ACTIVITY_MAX_INTERVAL_S",
        description="Maximum backoff interval in seconds for model activities",
        ge=10.0,
        le=300.0,
    )

    # Toolset activities - for get-tools/list-tools operations (toolset level)
    temporal_toolset_activity_max_attempts: int = Field(
        default=3,
        alias="TEMPORAL_TOOLSET_ACTIVITY_MAX_ATTEMPTS",
        description="Maximum retry attempts for toolset activities (get-tools/list-tools)",
        ge=1,
        le=5,
    )
    temporal_toolset_activity_initial_interval_s: float = Field(
        default=1.0,
        alias="TEMPORAL_TOOLSET_ACTIVITY_INITIAL_INTERVAL_S",
        description="Initial backoff interval in seconds for toolset activities",
        ge=0.1,
        le=10.0,
    )
    temporal_toolset_activity_backoff_coefficient: float = Field(
        default=1.5,
        alias="TEMPORAL_TOOLSET_ACTIVITY_BACKOFF_COEFFICIENT",
        description="Backoff coefficient for toolset activities",
        ge=1.0,
        le=3.0,
    )
    temporal_toolset_activity_max_interval_s: float = Field(
        default=10.0,
        alias="TEMPORAL_TOOLSET_ACTIVITY_MAX_INTERVAL_S",
        description="Maximum backoff interval in seconds for toolset activities",
        ge=1.0,
        le=60.0,
    )

    # Tool activities - for individual tool call execution (more conservative)
    temporal_tool_activity_max_attempts: int = Field(
        default=3,
        alias="TEMPORAL_TOOL_ACTIVITY_MAX_ATTEMPTS",
        description="Maximum retry attempts for individual tool call activities",
        ge=1,
        le=5,
    )
    temporal_tool_activity_initial_interval_s: float = Field(
        default=1.0,
        alias="TEMPORAL_TOOL_ACTIVITY_INITIAL_INTERVAL_S",
        description="Initial backoff interval in seconds for tool activities",
        ge=0.1,
        le=10.0,
    )
    temporal_tool_activity_backoff_coefficient: float = Field(
        default=1.5,
        alias="TEMPORAL_TOOL_ACTIVITY_BACKOFF_COEFFICIENT",
        description="Backoff coefficient for tool activities",
        ge=1.0,
        le=3.0,
    )
    temporal_tool_activity_max_interval_s: float = Field(
        default=10.0,
        alias="TEMPORAL_TOOL_ACTIVITY_MAX_INTERVAL_S",
        description="Maximum backoff interval in seconds for tool activities",
        ge=1.0,
        le=60.0,
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
