"""Pydantic models for codebase analysis output."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

# ──────────────────────────────────────────────
# 🔄 Extended Enums
# ──────────────────────────────────────────────


class InboundKind(str, Enum):
    HTTP = "http_endpoint"  # REST/HTTP 1.1/2/3 (incl. long-polling, /metrics)
    GRAPHQL = "graphql_service"  # HTTP for Q/M; subs via WS or SSE (see notes)
    GRPC = "grpc_service"  # Unary/streaming over HTTP/2(+)
    RPC_GENERIC = "rpc_service"  # Thrift/JSON-RPC/XML-RPC/custom RPC
    SOAP = "soap_service"

    WEBSOCKET = "websocket_endpoint"  # Bidirectional WS
    SSE = "server_sent_events_endpoint"  # text/event-stream

    WEBHOOK = "webhook_receiver"  # Third-party callbacks (Stripe, GH, etc.)
    MSG_CONSUMER = "message_consumer"  # Kafka/Rabbit/SQS/PubSub/Kinesis/JMS/MQ
    DB_CHANGEFEED = (
        "db_changefeed_consumer"  # Debezium/binlog/Mongo CS/DynamoDB streams
    )
    OBJECT_STORAGE_EVENT = "object_storage_event"  # S3/GCS/Azure Blob notifications

    MQTT_IOT_ENDPOINT = (
        "mqtt_iot_endpoint"  # MQTT broker/endpoint (AMQP1.0/CoAP -> map here if used)
    )
    WEBRTC_MEDIA = "webrtc_media_server"  # WebRTC SFU/MCU/DataChannel ingress
    TELECOM_SIGNALING = "telecom_signaling"  # SIP (voice), SMPP (SMS)

    UDP_SERVER = "udp_server"  # Syslog/StatsD/custom UDP
    TCP_RAW_SERVER = "tcp_raw_server"  # Non-HTTP framed/line protocols
    UNIX_SOCKET_SERVER = "unix_socket_server"  # Intra-host UDS (optional)

    SCHEDULE = "scheduler_trigger"  # Cron/Temporal/Celery beat
    CLI = "cli_command"
    FILE_WATCHER = "file_watcher"
    SFTP_FTP_SERVER = "sftp_ftp_server"
    EMAIL_INBOUND = "email_inbound"
    Other = "other"


class OutboundKind(str, Enum):
    HTTP = "http_client"  # REST/HTTP calls (incl. OAuth/OIDC, webhook POSTs)
    GRAPHQL = "graphql_client"  # GraphQL queries/mutations
    GRPC = "grpc_client"  # gRPC client
    RPC_GENERIC = "rpc_client"  # Thrift / JSON-RPC / XML-RPC clients
    SOAP = "soap_client"  # SOAP over HTTP client
    WEBSOCKET_CLIENT = "websocket_client"  # Outbound WS connections
    # Note: Use MSG_PRODUCER for classic pub/sub to a broker; use DB_STREAM
    # when treating the event log as a database/stream store (e.g., ksqlDB/Materialize/EventStoreDB).
    MSG_PRODUCER = "message_producer"  # Pub/sub producer to brokers (Kafka/Rabbit/SQS/PubSub/Kinesis)
    QUEUE_TASK = "task_queue_enqueue"  # Celery/Sidekiq/Resque job enqueue
    DB_SQL = "db_sql"  # Classic RDBMS (OLTP)
    DB_DISTSQ_HTAP = "db_dist_sql_htap"  # Spanner/Cockroach/Yugabyte/TiDB/SingleStore
    DB_NOSQL = "db_nosql"  # Key-value, document, wide-column. Examples: Redis/Aerospike/RocksDB/MongoDB/Couchbase/Cassandra/HBase/Scylla
    DB_GRAPH = "db_graph"  # Property or RDF graph. Examples: JanusGraph/Neptune/Stardog/Virtuoso
    DB_ANALYTIC_OLAP = "db_olap"  # Snowflake/BigQuery/Redshift/ClickHouse/Druid/Pinot
    DB_LAKEHOUSE = "db_lakehouse"  # Delta/Iceberg/Hudi (+ Spark/Trino)
    DB_TSDB = "db_timeseries"  # Influx/Timescale/Prometheus/VictoriaMetrics/QuestDB
    DB_VECTOR = "db_vector"  # Milvus/Pinecone/Weaviate/Qdrant/pgvector/ES k-NN
    DB_STREAM = "db_stream"  # Stream DB / log-as-database (ksqlDB/Materialize/EventStoreDB); treat stream as storage (append, materialized views)
    DB_SEARCH_INDEX = "db_search_index"  # Elasticsearch/OpenSearch/Solr
    DB_LEDGER = "db_ledger"  # QLDB/Hyperledger/Corda
    CACHE = "cache_operation"  # role/capability; often DB_KV in-memory
    FILE_STORAGE = "file_storage"  # S3/GCS/Azure Blob/Filesystem
    EMAIL = "email_service"  # SES/SendGrid/etc.
    SMS_PUSH = "notification_service"  # SMS/Push (Twilio/FCM/APNs)
    TELEMETRY = "telemetry_emit"  # Metrics/Traces/Logs (OTel/StatsD/Prom)
    Other = "other"


class ArtifactType(str, Enum):
    """Type of codebase."""

    APPLICATION = "application"
    LIBRARY = "library"


class BackendArchitecturalType(str, Enum):
    """Type of architectural pattern."""

    MICROSERVICES = "microservices"
    STREAMING = "streaming"
    BATCH = "batch"
    WORKFLOW = "workflow"
    SERVERLESS = "serverless"
    MONOLITH = "monolith"
    EVENT_DRIVEN = "event_driven"


class FrontendRenderingStrategyType(str, Enum):
    """Type of frontend rendering strategy."""

    SSR = "server side rendering"
    SSG = "static site generation"
    CSR = "client side rendering"
    ISR = "incremental static regeneration"
    STREAMING_SSR = "streaming server side rendering"
    PARTIAL_HYDRATION = "partial hydration - islands architecture"


class TargetLevel(str, Enum):
    """Target level for library feature analysis."""

    FUNCTION = "function"
    CLASS = "class"


class Concept(str, Enum):
    """Semantic concept for library feature analysis."""

    ANNOTATION_LIKE = "AnnotationLike"
    CALL_EXPRESSION = "CallExpression"
    INHERITANCE = "Inheritance"
    IMPORT = "Import"
    VARIABLE_ASSIGNMENT = "VariableAssignment"
    DECORATOR = "Decorator"
    ATTRIBUTE_ACCESS = "AttributeAccess"
    METHOD_CALL = "MethodCall"
    CLASS_DEFINITION = "ClassDefinition"
    FUNCTION_DEFINITION = "FunctionDefinition"


class LocatorStrategy(str, Enum):
    """Locator strategy for library feature analysis."""

    VARIABLE_BOUND = "VariableBound"
    DIRECT = "Direct"


# ──────────────────────────────────────────────
# 🔄 Supporting Models
# ──────────────────────────────────────────────


class ConfigFile(BaseModel):
    """Configuration file details."""

    path: str = Field(..., description="Configuration file path")
    purpose: str = Field(..., description="Purpose of the configuration file")

    model_config = ConfigDict(extra="forbid")


class ConstructQueryConfigKey(str, Enum):
    """Typed construct query configuration matching JSON schema structure."""

    method_regex = "MethodRegex"
    annotation_name_regex = "AnnotationNameRegex"
    attribute_regex = "AttributeRegex"
    callee_regex = "CalleeRegex"
    superclass_regex = "SuperclassRegex"

    model_config = ConfigDict(extra="forbid")


class LibraryFeatureSummary(BaseModel):
    """
    Human-readable feature summary with typed capability hints.
    No file locations here (avoid duplication with Interfaces).
    """

    feature_key: str = Field(
        ..., description="Stable key (e.g., 'fastapi.routing', 'sqlalchemy.orm')"
    )
    summary: str = Field(
        ..., description="2–3 line human summary of what this feature provides/does"
    )
    absolute_import_paths: List[str] = Field(
        ..., min_length=1, description="Fully qualified import paths"
    )
    target_level: TargetLevel = Field(..., description="function or class")
    concept: Concept = Field(
        ...,
        description="Semantic concept (AnnotationLike, CallExpression, Inheritance, etc.)",
    )
    locator_strategy: LocatorStrategy = Field(
        ..., description="VariableBound or Direct"
    )
    construct_query: Optional[Dict[ConstructQueryConfigKey, str]] = Field(
        default=None,
        description="Optional map of construct filters with regex patterns for matching program elements",
    )

    model_config = ConfigDict(extra="forbid")


class FrameworkLibraryOutput(BaseModel):
    name: str
    description: str
    version: Optional[str] = None
    documentation_url: Optional[str] = None
    features_used: List[LibraryFeatureSummary]

    model_config = ConfigDict(extra="forbid")


class CommandKind(str, Enum):
    """Category for a development workflow command."""

    BUILD = "build"
    DEV = "dev"
    TEST = "test"
    LINT = "lint"
    TYPE_CHECK = "type_check"


class CommandSpec(BaseModel):
    """Uniform specification for any development workflow command."""

    kind: CommandKind = Field(..., description="Category of the command")
    command: str = Field(..., description="Full runnable command string")
    description: Optional[str] = Field(None, description="Short human-friendly summary")

    config_files: List[str] = Field(
        default_factory=list,
        description="Relevant config files with relative path to the codebase root",
    )

    model_config = ConfigDict(extra="forbid")


class CoreFile(BaseModel):
    """Core business logic data model details."""

    path: str = Field(..., description="File path")
    responsibility: Optional[str] = Field(
        None, description="Responsibilities of data models covered in the file"
    )

    model_config = ConfigDict(extra="forbid")


class BusinessLogicDomain(BaseModel):
    """Business logic domain details."""

    description: str = Field(
        ..., description="Domain description based on data models across the codebase"
    )
    data_models: List[CoreFile] = Field(..., description="Data models for this domain")

    model_config = ConfigDict(extra="forbid")


class DependencyGuideEntry(BaseModel):
    """Documentation entry for a single dependency."""

    name: str = Field(..., description="Library name (exact match to input)")
    purpose: str = Field(..., description="1-2 lines from official docs describing what this library does")
    usage: str = Field(
        ...,
        description="Exactly 2 sentences describing core features and capabilities",
    )

    model_config = ConfigDict(extra="forbid")


class DependencyGuide(BaseModel):
    """Collection of dependency documentation entries for a codebase."""

    dependencies: List[DependencyGuideEntry] = Field(
        default_factory=list,
        description="List of documented dependencies with purpose and usage information",
    )

    model_config = ConfigDict(extra="forbid")


# ──────────────────────────────────────────────
# 🔄 Main Output Models
# ──────────────────────────────────────────────


class CodebaseMetadataOutput(BaseModel):
    """Codebase metadata information."""

    codebase_type: ArtifactType = Field(..., description="Type of codebase")
    architectural_pattern: Optional[List[BackendArchitecturalType]] = Field(
        None,
        description="Type of architectural pattern if current codebase is of type backend",
    )
    frontend_rendering_strategy: Optional[FrontendRenderingStrategyType] = Field(
        None,
        description="Type of frontend rendering strategy if current codebase if of type frontend",
    )
    description: str = Field(..., description=" Short Description of the codebase")

    model_config = ConfigDict(extra="forbid")


class ProgrammingLanguageMetadataOutput(BaseModel):
    """Programming language metadata with extended package manager support."""

    primary_language: str = Field(..., description="Primary programming language")
    package_manager: str = Field(
        ..., description="Package manager used for the project,"
    )

    model_config = ConfigDict(extra="forbid")


class ProjectConfiguration(BaseModel):
    """Project structure information."""

    config_files: List[ConfigFile] = Field(
        ...,
        description=(
            "Complete list of configuration files (lint, test, package manager, build, deploy, etc). "
            "Include every relevant config file; do not omit any."
        ),
    )

    model_config = ConfigDict(extra="forbid")


class DevelopmentWorkflow(BaseModel):
    """Development workflow configuration with a unified command list."""

    commands: List[CommandSpec] = Field(
        ...,
        description=(
            "Complete list of workflow commands; include all build/dev/test/lint/type_check commands found."
        ),
    )
    model_config = ConfigDict(extra="forbid")


class InboundConstruct(BaseModel):
    kind: InboundKind = Field(..., description="Kind of inbound construct")
    library: Optional[str] = Field(
        ...,
        description="Library/Framework used for the inbound construct if applicable.",
    )
    match_pattern: Dict[str, List[str]] = Field(
        ...,
        description="relative w.r.t codebase path - File path as key with corresponding list of match patterns where the inbound construct is used",
    )
    model_config = ConfigDict(extra="forbid")


class OutboundConstruct(BaseModel):
    kind: OutboundKind = Field(..., description="Kind of outbound construct")
    library: Optional[str] = Field(
        ...,
        description="Library/Framework used for the outbound construct if applicable.",
    )
    match_pattern: Dict[str, List[str]] = Field(
        ...,
        description="relative w.r.t codebase path - File path as key with corresponding list of match patterns where the outbound construct is used",
    )
    model_config = ConfigDict(extra="forbid")


class Interfaces(BaseModel):
    """Interaces used in the codebase"""

    inbound_constructs: List[InboundConstruct] = Field(
        default_factory=list,
        description=(
            "External-facing entry points that RECEIVE traffic into this codebase across its service boundary "
            "(e.g., HTTP/gRPC routes, GraphQL resolvers, WebSocket endpoints, webhooks, CLI commands, "
            "scheduled jobs, message/stream consumers).  "
        ),
    )

    outbound_constructs: List[OutboundConstruct] = Field(
        default_factory=list,
        description=(
            "Calls this codebase EMITS to external systems across its service boundary "
            "(e.g., HTTP/gRPC clients, message/stream producers, SQL/NoSQL DB operations, cache ops, "
            "object storage, search, email/notifications, telemetry)."
        ),
    )


class AgentMdOutput(BaseModel):
    """Complete codebase analysis output matching the JSON specification."""

    # TODO: remove optional when ready
    codebase_metadata: Optional[CodebaseMetadataOutput] = Field(
        default=None, description="Codebase metadata"
    )
    programming_language_metadata: ProgrammingLanguageMetadataOutput = Field(
        ..., description="Programming language metadata"
    )
    project_configuration: ProjectConfiguration = Field(
        ..., description="Project configuration"
    )
    # TODO: remove optional when ready
    frameworks_and_libraries: Optional[List[FrameworkLibraryOutput]] = Field(
        default=None,
        description="frameworks and libraries used and the overview of the functionality they provide.",
    )
    development_workflow: DevelopmentWorkflow = Field(
        ...,
        description="Development workflow configuration including build, test, lint commands ",
    )
    dependency_guide: Optional[DependencyGuide] = Field(
        default=None,
        description="Documentation entries for codebase dependencies with purpose and usage",
    )
    business_logic: BusinessLogicDomain = Field(
        ..., description="Critical business logic domains"
    )
    # TODO: remove optional when ready
    app_interfaces: Optional[Interfaces] = Field(
        default=None,
        description="Inbound or/and outboundInteraces used in the codebase",
    )

    model_config = ConfigDict(extra="forbid")
