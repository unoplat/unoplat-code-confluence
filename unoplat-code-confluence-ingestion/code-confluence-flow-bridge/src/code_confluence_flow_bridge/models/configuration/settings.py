# Standard Library
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

# Third Party
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import from commons package


class DatabaseType(str, Enum):
    NEO4J = "neo4j"


# ──────────────────────────────────────────────────────────────────────────────
# CODEBASE DETECTION MODELS (moved from POC)
# ──────────────────────────────────────────────────────────────────────────────


class FileNode(BaseModel):
    """A single path from the repository inventory."""

    path: str  # e.g. "src/foo/__init__.py"
    kind: Literal["file", "dir"]
    size: Optional[int] = None  # bytes (None for directories)


class Signature(BaseModel):
    """
    A test applied to the set of filenames in a directory, or to the file
    contents if 'contains' is supplied.
    """

    file: Optional[str] = None  # exact filename to look for
    contains: Optional[str] = None  # substring that must appear in that file
    contains_absence: Optional[List[str]] = (
        None  # substrings that must NOT appear in file
    )
    glob: Optional[str] = None  # shell-style wildcard pattern


class ManagerRule(BaseModel):
    """Package manager detection rule."""

    manager: str  # "poetry", "pip", "maven", …
    weight: int = 1  # for tie-breaking / confidence
    signatures: List[Signature] = Field(default_factory=list)
    workspace_field: Optional[str] = (
        None  # e.g. "workspaces" for npm, "tool.uv.workspace" for uv
    )


class LanguageRules(BaseModel):
    """Language-specific detection rules."""

    ignores: List[str]  # dir tokens to drop if not referenced
    managers: List[ManagerRule]


class CodebaseDetection(BaseModel):
    """Simple codebase detection result."""

    path: str  # relative path from repository root
    programming_language: str  # "python"
    package_manager: str  # "poetry" | "pip" | "uv"


# ──────────────────────────────────────────────────────────────────────────────
# EXISTING CONFIGURATION MODELS (BaseModel for JSON config)
# ──────────────────────────────────────────────────────────────────────────────

# RepositorySettings and CodebaseConfig now imported from commons above


class LLMProviderConfig(BaseModel):
    llm_model_provider: str
    llm_model_provider_args: Dict[str, Any]


# Environment Settings (BaseSettings for environment variables)
class EnvironmentSettings(BaseSettings):
    """Environment variables and secrets"""

    model_config = SettingsConfigDict(
        # env_prefix="UNOPLAT_",
        env_file=(".env.dev", ".env.test", ".env.prod"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields
        populate_by_name=True,
        env_parse_none_str=None,  # Changed from list to None to fix type error
    )

    neo4j_host: str = Field(default="localhost", alias="NEO4J_HOST")

    neo4j_port: int = Field(default=7687, alias="NEO4J_PORT")

    neo4j_username: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: SecretStr = Field(
        default=SecretStr("password"), alias="NEO4J_PASSWORD"
    )

    neo4j_max_connection_lifetime: int = Field(
        default=3600,
        alias="NEO4J_MAX_CONNECTION_LIFETIME",
        description="The maximum lifetime of a connection to the Neo4j database in seconds",
    )

    neo4j_max_connection_pool_size: int = Field(
        default=50,
        alias="NEO4J_MAX_CONNECTION_POOL_SIZE",
        description="The maximum number of connections in the Neo4j connection pool",
    )

    neo4j_connection_acquisition_timeout: int = Field(
        default=60,
        alias="NEO4J_CONNECTION_ACQUISITION_TIMEOUT",
        description="The maximum time to wait for a connection to be acquired from the Neo4j connection pool in seconds",
    )

    # Temporal worker concurrency settings
    temporal_max_concurrent_activities: int = Field(
        default=4,
        alias="TEMPORAL_MAX_CONCURRENT_ACTIVITIES",
        description="The maximum number of activity tasks that the worker will execute concurrently",
    )

    temporal_max_concurrent_activity_task_polls: int = Field(
        default=2,
        alias="TEMPORAL_MAX_CONCURRENT_ACTIVITY_TASK_POLLS",
        description="The maximum number of concurrent poll requests the worker will make to the Temporal service for activity tasks",
    )

    # Temporal workflow task poller autoscaling settings
    temporal_workflow_poller_min: int = Field(
        default=1,
        alias="TEMPORAL_WORKFLOW_POLLER_MIN",
        description="The minimum number of workflow task pollers that will always be attempted (assuming slots are available)",
    )

    temporal_workflow_poller_initial: int = Field(
        default=2,
        alias="TEMPORAL_WORKFLOW_POLLER_INITIAL",
        description="The initial number of workflow task pollers before autoscaling kicks in (must be between min and max)",
    )

    temporal_workflow_poller_max: int = Field(
        default=4,
        alias="TEMPORAL_WORKFLOW_POLLER_MAX",
        description="The maximum number of workflow task pollers that can be open at once",
    )

    # Temporal activity task poller autoscaling settings
    temporal_activity_poller_min: int = Field(
        default=1,
        alias="TEMPORAL_ACTIVITY_POLLER_MIN",
        description="The minimum number of activity task pollers that will always be attempted (assuming slots are available)",
    )

    temporal_activity_poller_initial: int = Field(
        default=2,
        alias="TEMPORAL_ACTIVITY_POLLER_INITIAL",
        description="The initial number of activity task pollers before autoscaling kicks in (must be between min and max)",
    )

    temporal_activity_poller_max: int = Field(
        default=4,
        alias="TEMPORAL_ACTIVITY_POLLER_MAX",
        description="The maximum number of activity task pollers that can be open at once",
    )

    # Flag to enable/disable poller autoscaling
    temporal_enable_poller_autoscaling: bool = Field(
        default=False,
        alias="TEMPORAL_ENABLE_POLLER_AUTOSCALING",
        description="Whether to enable autoscaling for workflow and activity task pollers",
    )

    # Generic codebase parser configuration
    codebase_parser_file_batch_size: int = Field(
        default=1000,
        alias="CODEBASE_PARSER_FILE_BATCH_SIZE",
        description="Number of files to process in a single Neo4j UNWIND batch operation. Optimal for performance vs memory usage.",
        ge=100,  # minimum 100
        le=5000,  # maximum 5000
    )

    codebase_parser_package_batch_size: int = Field(
        default=500,
        alias="CODEBASE_PARSER_PACKAGE_BATCH_SIZE",
        description="Number of packages to create in a single batch operation. Smaller than file batch due to hierarchical relationships.",
        ge=50,  # minimum 50
        le=2000,  # maximum 2000
    )

    codebase_parser_insertion_queue_size: int = Field(
        default=2000,
        alias="CODEBASE_PARSER_INSERTION_QUEUE_SIZE",
        description="Maximum size of the asyncio queue for file insertion batches. Should be at least 2x file_batch_size for optimal throughput.",
        ge=200,  # minimum 200
        le=10000,  # maximum 10000
    )

    codebase_parser_max_retry_wait: int = Field(
        default=30,
        alias="CODEBASE_PARSER_MAX_RETRY_WAIT",
        description="Maximum wait time in seconds for exponential backoff when Neo4j operations fail",
        ge=5,  # minimum 5 seconds
        le=300,  # maximum 5 minutes
    )

    codebase_parser_initial_retry_wait: float = Field(
        default=1.0,
        alias="CODEBASE_PARSER_INITIAL_RETRY_WAIT",
        description="Initial wait time in seconds for exponential backoff when Neo4j operations fail",
        ge=0.1,  # minimum 0.1 seconds
        le=10.0,  # maximum 10 seconds
    )

    # Repository storage configuration
    repositories_base_path: str = Field(
        default="~/.unoplat/repositories",
        alias="REPOSITORIES_BASE_PATH",
        description="Base directory path for storing cloned repositories. Use '~' for user home directory expansion.",
    )

    # Framework definitions configuration
    framework_definitions_path: str = Field(
        default="/framework-definitions",
        alias="FRAMEWORK_DEFINITIONS_PATH",
        description="Absolute path to framework definitions directory containing language-specific definition files",
    )

    # File processing concurrency configuration
    codebase_parser_file_processing_concurrency: int = Field(
        default=3,
        alias="CODEBASE_PARSER_FILE_PROCESSING_CONCURRENCY",
        description="Maximum number of files to process concurrently during parsing. Controls memory usage and CPU utilization.",
        ge=1,  # minimum 1 file at a time
        le=50,  # maximum 50 concurrent files
    )

    # GitHub App manifest onboarding configuration
    github_app_manifest_template_path: str = Field(
        default="/opt/unoplat/github-app-config/manifest-template.json",
        alias="GITHUB_APP_MANIFEST_TEMPLATE_PATH",
        description="Absolute path to the GitHub App manifest template file mounted into the container.",
    )

    github_app_name: str = Field(
        default="Unoplat Code Confluence",
        alias="GITHUB_APP_NAME",
        description="Default name applied to the GitHub App manifest when the template omits a name.",
    )

    github_app_homepage_url: Optional[str] = Field(
        default=None,
        alias="GITHUB_APP_HOMEPAGE_URL",
        description="Fallback homepage URL injected into the manifest when not provided by the template or request.",
    )

    github_app_description: Optional[str] = Field(
        default=None,
        alias="GITHUB_APP_DESCRIPTION",
        description="Fallback description applied to the manifest when not provided elsewhere.",
    )

    github_app_redirect_path: str = Field(
        default="/integrations/github/app-manifest/callback",
        alias="GITHUB_APP_REDIRECT_PATH",
        description="Path exposed by this service to receive GitHub's manifest conversion callback.",
    )

    github_app_webhook_path: str = Field(
        default="/integrations/github/webhook",
        alias="GITHUB_APP_WEBHOOK_PATH",
        description="Path exposed by this service to receive GitHub webhook deliveries.",
    )

    github_app_owner_type: Literal["user", "organization"] = Field(
        default="user",
        alias="GITHUB_APP_OWNER_TYPE",
        description="Default owner type used when building installation URLs ('user' or 'organization').",
    )

    github_app_owner: Optional[str] = Field(
        default=None,
        alias="GITHUB_APP_OWNER",
        description="Default GitHub username or organization slug to register the app under when omitted in requests.",
    )

    github_app_manifest_state_ttl_minutes: int = Field(
        default=30,
        alias="GITHUB_APP_MANIFEST_STATE_TTL_MINUTES",
        description="Time-to-live for stored manifest states awaiting GitHub callbacks.",
        ge=1,
        le=1440,
    )
