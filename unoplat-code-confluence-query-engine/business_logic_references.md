# Business Logic References

## Domain Summary
This codebase is centered on AI-assisted codebase analysis and repository workflow orchestration. Its data models cover AI provider and OAuth configuration, MCP/tool setup, repository metadata and rulesets, Temporal agent dependencies, workflow envelopes, event telemetry, and usage statistics. It produces structured outputs such as engineering workflows, dependency guides, AGENTS.md updates, and framework-feature validation records.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py#L55-L61` — `class CodexOAuthAuthorizeResponse(BaseModel):
    """Response payload for OAuth authorize flow initialization."""

    flow_id: str
    authorization_url: str
    expires_at: int
    poll_interval_ms: int`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py#L64-L67` — `class CodexOAuthAuthorizeRequest(BaseModel):
    """Optional payload for OAuth authorize URL generation."""

    frontend_origin: Optional[str] = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py#L70-L74` — `class CodexOAuthFlowStatusResponse(BaseModel):
    """Polling response for OAuth flow state."""

    status: str
    error: Optional[str] = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py#L77-L83` — `class CodexOAuthConnectionStatusResponse(BaseModel):
    """Current stored OAuth connection state for codex_openai."""

    connected: bool
    account_id: Optional[str] = None
    expires_at: Optional[int] = None
    configured_at: Optional[datetime] = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py#L86-L90` — `class CodexOAuthDeleteResponse(BaseModel):
    """Response payload for OAuth disconnect endpoint."""

    deleted: bool
    message: str`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/app_feedback.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/app_feedback.py#L21-L27` — `class AppFeedbackRequest(BaseModel):
    category: AppFeedbackCategory
    sentiment: SentimentRating
    subject: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10, max_length=2000)
    current_route: Optional[str] = None
    app_version: Optional[str] = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/app_feedback.py#L30-L32` — `class AppFeedbackResponse(BaseModel):
    issue_url: Optional[str] = None
    issue_number: Optional[int] = None`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py#L63-L67` — `class RepositoryWorkflowRunResponse(BaseModel):
    """Response returned when a repository Temporal workflow is launched."""

    repository_workflow_run_id: str
    trace_id: str`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py#L70-L75` — `class RepositoryAgentRunCancelResponse(BaseModel):
    """Response returned when a repository agent workflow cancel is requested."""

    repository_workflow_run_id: str
    status: Literal["cancel_requested"]
    message: str`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py#L78-L85` — `class RepositoryAgentMdPrRequest(BaseModel):
    """Request payload to manually create/update AGENTS.md PR."""

    owner_name: str = Field(..., min_length=1)
    repo_name: str = Field(..., min_length=1)
    repository_workflow_run_id: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py#L88-L96` — `class RepositoryAgentMdPrResponse(BaseModel):
    """Response payload for manual AGENTS.md PR endpoint."""

    status: Literal["modified", "no_changes"]
    pr_url: str | None = None
    pr_number: int | None = None
    branch_name: str | None = None
    changed_files: list[str] = Field(default_factory=list)
    message: str`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py#L99-L103` — `class RepositoryAgentMdPrStatusResponse(BaseModel):
    """Response payload for GET /repository-agent-md-pr status check."""

    exists: bool
    pr_metadata: RepositoryAgentMdPrResponse | None = None`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py#L15-L18` — `class FlagUpdateRequest(BaseModel):
    """Request model for updating flag status."""

    status: bool`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py#L41-L46` — `class ToolConfigResponse(BaseModel):
    """Response for tool configuration status (never returns secrets)."""

    provider: ToolProvider
    status: ToolConfigStatus
    configured_at: Optional[datetime] = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py#L49-L52` — `class ToolConfigListResponse(BaseModel):
    """Response listing all tool configurations."""

    tools: list[ToolConfigResponse] = Field(default_factory=list)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py#L55-L58` — `class ToolConfigDeleteResponse(BaseModel):
    """Response for successful tool configuration deletion."""

    message: str`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/ai_model_config.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/ai_model_config.py#L12-L35` — `class AiModelConfig(SQLBase):
    """AI model provider configuration. Single active configuration only."""

    __tablename__ = "ai_model_config"

    # Single record approach - always id=1 for the active config
    id: Mapped[int] = mapped_column(default=1, primary_key=True)
    provider_key: Mapped[str] = mapped_column(comment="Provider identifier")
    model_name: Mapped[str] = mapped_column(comment="Model name/identifier")
    provider_kind: Mapped[str] = mapped_column(comment="native | openai_compat")
    base_url: Mapped[Optional[str]] = mapped_column(
        default=None, comment="Custom endpoint URL"
    )
    profile_key: Mapped[Optional[str]] = mapped_column(
        default=None, comment="Pydantic AI profile"
    )
    extra_config: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict, comment="Provider-specific configuration"
    )
    model_params: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict, comment="Inference params: temperature, top_p, max_tokens, request_limit, etc."
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_business_logic_repository.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_business_logic_repository.py#L46-L50` — `class _DataModelSpan(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    identifier: str | None = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_business_logic_repository.py#L53-L85` — `class _DataModelPositionsPayload(BaseModel):
    positions: dict[str, tuple[int, int]] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, data: object) -> object:
        if isinstance(data, Mapping):
            if "positions" in data:
                return data
            return {"positions": data}
        return data

    @field_validator("positions", mode="before")
    @classmethod
    def normalize_positions(cls, value: object) -> dict[str, tuple[int, int]]:
        if not isinstance(value, Mapping):
            return {}
        positions: dict[str, tuple[int, int]] = {}
        for key, entry in value.items():
            if not isinstance(key, str):
                continue
            if not isinstance(entry, Sequence) or isinstance(entry, (str, bytes)):
                continue
            if len(entry) != 2:
                continue
            start_val = entry[0]
            end_val = entry[1]
            if not isinstance(start_val, int) or not isinstance(end_val, int):
                continue
            if start_val == end_val:
                continue
            positions[key] = (start_val, end_val)
        return positions`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/config/ai_model_config.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/config/ai_model_config.py#L17-L23` — `class ModelParams(BaseModel):
    """Validated inference parameters stored in the JSONB model_params column."""

    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    request_limit: Optional[int] = Field(None, gt=0, le=1000)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/config/ai_model_config.py#L26-L38` — `class AiModelConfigBase(BaseModel):
    """Base model with common AI configuration fields."""

    provider_key: str
    model_name: str
    # Optional top-level hint for providers that support a nested provider (e.g., HuggingFace)
    # This is persisted under `extra_config.provider_name` for storage/back-compat
    provider_name: Optional[str] = None
    provider_kind: Optional[ProviderKind] = None
    base_url: Optional[str] = None
    profile_key: Optional[str] = None
    extra_config: Dict[str, Any] = Field(default_factory=dict)
    model_params: Optional[ModelParams] = None`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/config/mcp_config.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/config/mcp_config.py#L26-L52` — `class LocalMCPServerConfig(BaseModel):
    """Configuration for local MCP servers using stdio transport."""

    server_type: Literal[MCPServerType.LOCAL] = MCPServerType.LOCAL
    command: list[str] = Field(..., description="Command to run the MCP server")
    args: list[str] = Field(
        default_factory=list, description="Additional arguments for the command"
    )
    environment: dict[str, str] = Field(
        default_factory=dict, description="Environment variables for the server"
    )
    cwd: str | None = Field(
        default=None, description="Working directory for the server process"
    )
    timeout: int = Field(
        default=5, description="Timeout in seconds for server initialization"
    )
    tool_prefix: str | None = Field(
        default=None, description="Prefix for tool names from this server"
    )

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Command cannot be empty")
        return v`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/config/mcp_config.py#L55-L76` — `class RemoteMCPServerConfig(BaseModel):
    """Configuration for remote MCP servers using HTTP SSE transport."""

    server_type: Literal[MCPServerType.REMOTE] = MCPServerType.REMOTE
    url: str = Field(..., description="SSE endpoint URL for the MCP server")
    headers: dict[str, str] = Field(
        default_factory=dict, description="HTTP headers for authentication"
    )
    timeout: int = Field(default=5, description="Initial connection timeout in seconds")
    tool_prefix: str | None = Field(
        default=None, description="Prefix for tool names from this server"
    )
    protocol: MCPServerProtocol = Field(
        default=MCPServerProtocol.SSE, description="Protocol to use for communication"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/config/mcp_config.py#L85-L106` — `class MCPServersConfig(BaseModel):
    """Configuration for multiple MCP servers."""

    servers: dict[str, MCPServerConfigUnion] = Field(
        default_factory=dict, description="Named MCP server configurations"
    )

    def get_local_servers(self) -> dict[str, LocalMCPServerConfig]:
        """Get all local MCP server configurations."""
        return {
            name: config
            for name, config in self.servers.items()
            if config.server_type == MCPServerType.LOCAL
        }

    def get_remote_servers(self) -> dict[str, RemoteMCPServerConfig]:
        """Get all remote MCP server configurations."""
        return {
            name: config
            for name, config in self.servers.items()
            if config.server_type == MCPServerType.REMOTE
        }`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/events/agent_events.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/events/agent_events.py#L22-L34` — `class AgentEventPayload(BaseModel):
    """Snapshot of the latest agent event per codebase."""

    model_config = ConfigDict(extra="forbid")

    id: int
    event: str
    phase: str
    message: Optional[str] = None
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_args: Optional[dict[str, Any]] = None
    tool_result_content: Optional[str] = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/events/agent_events.py#L37-L44` — `class CodebaseEventDelta(BaseModel):
    """Delta for an individual codebase when a new event arrives."""

    model_config = ConfigDict(extra="forbid")

    codebase_name: str
    progress: Percentage
    new_event: AgentEventPayload`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/events/agent_events.py#L47-L54` — `class RepositoryAgentEventDelta(BaseModel):
    """Delta payload for repository-level agent progress updates."""

    model_config = ConfigDict(extra="forbid")

    repository_name: str
    overall_progress: Percentage
    codebase_delta: CodebaseEventDelta`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L117-L125` — `class CoreFile(BaseModel):
    """Core business logic data model details."""

    path: str = Field(..., description="File path")
    responsibility: Optional[str] = Field(
        None, description="Responsibilities of data models covered in the file"
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L128-L136` — `class BusinessLogicDomain(BaseModel):
    """Business logic domain details."""

    description: str = Field(
        ..., description="Domain description based on data models across the codebase"
    )
    data_models: List[CoreFile] = Field(..., description="Data models for this domain")

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L139-L152` — `class DependencyGuideEntry(BaseModel):
    """Documentation entry for a single dependency."""

    name: str = Field(..., description="Library name (exact match to input)")
    purpose: str = Field(
        ...,
        description="1-2 lines from official docs describing what this library does",
    )
    usage: str = Field(
        ...,
        description="Exactly 2 sentences describing core features and capabilities",
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L155-L163` — `class DependencyGuide(BaseModel):
    """Collection of dependency documentation entries for a codebase."""

    dependencies: List[DependencyGuideEntry] = Field(
        default_factory=list,
        description="List of documented dependencies with purpose and usage information",
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L171-L185` — `class CodebaseMetadataOutput(BaseModel):
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

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L188-L196` — `class ProgrammingLanguageMetadataOutput(BaseModel):
    """Programming language metadata with extended package manager support."""

    primary_language: str = Field(..., description="Primary programming language")
    package_manager: str = Field(
        ..., description="Package manager used for the project,"
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L199-L209` — `class InboundConstruct(BaseModel):
    kind: InboundKind = Field(..., description="Kind of inbound construct")
    library: Optional[str] = Field(
        ...,
        description="Library/Framework used for the inbound construct if applicable.",
    )
    match_pattern: Dict[str, List[str]] = Field(
        ...,
        description="relative w.r.t codebase path - File path as key with corresponding list of match patterns where the inbound construct is used",
    )
    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L212-L222` — `class OutboundConstruct(BaseModel):
    kind: OutboundKind = Field(..., description="Kind of outbound construct")
    library: Optional[str] = Field(
        ...,
        description="Library/Framework used for the outbound construct if applicable.",
    )
    match_pattern: Dict[str, List[str]] = Field(
        ...,
        description="relative w.r.t codebase path - File path as key with corresponding list of match patterns where the outbound construct is used",
    )
    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L225-L239` — `class InternalConstruct(BaseModel):
    """Internal framework feature construct (non-inbound/outbound)."""

    kind: str = Field(
        ..., description="Feature key identifying this internal construct"
    )
    library: Optional[str] = Field(
        ...,
        description="Library/Framework used for the internal construct if applicable.",
    )
    match_pattern: Dict[str, List[str]] = Field(
        ...,
        description="Codebase-relative file path as key with corresponding list of match patterns",
    )
    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L242-L266` — `class Interfaces(BaseModel):
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

    internal_constructs: List[InternalConstruct] = Field(
        default_factory=list,
        description="Internal framework features that are neither inbound nor outbound constructs",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py#L269-L296` — `class AgentMdOutput(BaseModel):
    """Complete codebase analysis output matching the JSON specification."""

    # TODO: remove optional when ready
    codebase_metadata: Optional[CodebaseMetadataOutput] = Field(
        default=None, description="Codebase metadata"
    )
    programming_language_metadata: ProgrammingLanguageMetadataOutput = Field(
        ..., description="Programming language metadata"
    )
    engineering_workflow: EngineeringWorkflow = Field(
        default_factory=EngineeringWorkflow,
        description="Canonical engineering workflow with config and command inventory",
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

    model_config = ConfigDict(extra="forbid")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agents_md_updater_output.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agents_md_updater_output.py#L20-L36` — `class UpdaterFileChange(BaseModel):
    """Summary metadata for one updater-managed file."""

    path: str = Field(..., description="Absolute file path within codebase root")
    changed: bool = Field(..., description="Whether file content changed this run")
    change_type: Literal["created", "updated", "unchanged"] = Field(
        ..., description="Change classification for this file"
    )
    change_summary: str = Field(
        ..., description="Concise summary of the applied or detected change"
    )
    content_sha256: str | None = Field(
        default=None,
        description="Optional SHA-256 hash of final file content (no raw content persisted)",
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agents_md_updater_output.py#L39-L54` — `class AgentsMdUpdaterOutput(BaseModel):
    """Top-level output produced by AGENTS updater agent."""

    status: Literal["updated", "no_changes"] = Field(
        ..., description="Overall updater status"
    )
    touched_file_paths: list[str] = Field(
        default_factory=list,
        description="Absolute file paths touched by updater tools",
    )
    file_changes: list[UpdaterFileChange] = Field(
        default_factory=list,
        description="Summary metadata for each managed file",
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agents_md_updater_output.py#L57-L64` — `class SectionUpdaterRunRecord(BaseModel):
    """Record of a single section-scoped updater run, stored in workflow results."""

    section_id: SectionId = Field(..., description="Section identifier (e.g., 'engineering_workflow')")
    agent_name: str = Field(..., description="Agent name used for event tracking")
    output: AgentsMdUpdaterOutput = Field(..., description="Updater output for this section")

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agents_md_updater_output.py#L67-L78` — `class ManagedBlockRunRecord(BaseModel):
    """Record of a managed-block lifecycle step (e.g., bootstrap), stored in workflow results."""

    lifecycle_step: Literal["bootstrap"] = Field(
        ..., description="Lifecycle step identifier"
    )
    agent_name: str = Field(..., description="Agent/activity name for event tracking")
    output: AgentsMdUpdaterOutput = Field(
        ..., description="File-change output from this lifecycle step"
    )

    model_config = ConfigDict(extra="forbid")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/engineering_workflow_output.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/engineering_workflow_output.py#L20-L40` — `class EngineeringWorkflowCommand(BaseModel):
    """Canonical workflow command entry with citation-validated confidence."""

    command: str = Field(..., description="Runnable command")
    stage: EngineeringWorkflowStage = Field(..., description="Execution stage")
    config_file: str = Field(
        ..., description="Repository-root-relative path to the most relevant config file, or 'unknown'"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Citation-validated confidence score"
    )
    working_directory: Optional[str] = Field(
        default=None,
        description=(
            "Repository-root-relative directory from which command should execute. "
            "None/omitted = codebase root, '.' = repository root, "
            "nested path = specific workspace root."
        ),
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/engineering_workflow_output.py#L43-L51` — `class EngineeringWorkflow(BaseModel):
    """Canonical engineering workflow contract."""

    commands: List[EngineeringWorkflowCommand] = Field(
        default_factory=list,
        description="Canonical list of engineering commands",
    )

    model_config = ConfigDict(extra="forbid")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/git_ref_info.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/git_ref_info.py#L8-L14` — `class GitRefInfo(BaseModel):
    """Resolved default branch and head commit SHA for freshness metadata."""

    default_branch: str
    head_commit_sha: str

    model_config = ConfigDict(frozen=True, extra="forbid")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py#L18-L53` — `class FrameworkFeatureUsageIdentity(BaseModel):
    """Primary-key identity for code_confluence_file_framework_feature rows."""

    file_path: str
    feature_language: str
    feature_library: str
    feature_capability_key: str
    feature_operation_key: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    model_config = ConfigDict(frozen=True)

    @property
    def feature_key(self) -> str:
        """Display-only dotted convenience key."""
        return f"{self.feature_capability_key}.{self.feature_operation_key}"

    @model_validator(mode="after")
    def validate_line_span(self) -> FrameworkFeatureUsageIdentity:
        if self.end_line < self.start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return self

    def with_feature_identity(
        self,
        feature_capability_key: str,
        feature_operation_key: str,
    ) -> FrameworkFeatureUsageIdentity:
        """Return a copy with a different structured feature identity."""
        return self.model_copy(
            update={
                "feature_capability_key": feature_capability_key,
                "feature_operation_key": feature_operation_key,
            }
        )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py#L56-L88` — `class FrameworkFeatureValidationEvidenceUpsertRequest(BaseModel):
    """Repository input for evidence/confidence upsert operation."""

    identity: FrameworkFeatureUsageIdentity
    decision: FrameworkFeatureValidationDecision
    final_confidence: float = Field(ge=0.0, le=1.0)
    evidence_json: dict[str, object] = Field(default_factory=dict)
    updated_feature_capability_key: str | None = None
    updated_feature_operation_key: str | None = None

    @model_validator(mode="after")
    def validate_correct_decision_fields(
        self,
    ) -> FrameworkFeatureValidationEvidenceUpsertRequest:
        if self.decision == FrameworkFeatureValidationDecision.CORRECT:
            if not self.updated_feature_capability_key:
                raise ValueError(
                    "updated_feature_capability_key is required when decision='correct'"
                )
            if not self.updated_feature_operation_key:
                raise ValueError(
                    "updated_feature_operation_key is required when decision='correct'"
                )
            if (
                self.updated_feature_capability_key
                == self.identity.feature_capability_key
                and self.updated_feature_operation_key
                == self.identity.feature_operation_key
            ):
                raise ValueError(
                    "Updated structured feature identity must differ from identity fields"
                )
        return self`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py#L91-L96` — `class FrameworkFeatureValidationEvidenceUpsertResult(BaseModel):
    """Result summary for evidence/confidence upsert operations."""

    source_row_updated: bool
    corrected_row_upserted: bool
    corrected_identity: FrameworkFeatureUsageIdentity | None = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py#L99-L104` — `class FrameworkFeatureValidationStatusTransitionRequest(BaseModel):
    """Repository input for status-only transition operation."""

    identity: FrameworkFeatureUsageIdentity
    target_status: ValidationStatus
    expected_current_status: ValidationStatus | None = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py#L107-L112` — `class FrameworkFeatureValidationStatusTransitionResult(BaseModel):
    """Result summary for status transition operations."""

    status: str
    previous_status: ValidationStatus
    current_status: ValidationStatus`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py#L115-L127` — `class FrameworkFeatureValidationCandidate(BaseModel):
    """Low-confidence CallExpression usage candidate for validator execution."""

    identity: FrameworkFeatureUsageIdentity
    concept: str
    match_confidence: float = Field(ge=0.0, le=1.0)
    validation_status: ValidationStatus
    match_text: str | None = None
    evidence_json: dict[str, object] | None = None
    base_confidence: float = Field(ge=0.0, le=1.0)
    notes: str | None = None
    construct_query: dict[str, object] | None = None
    absolute_paths: list[str] = Field(default_factory=list)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py#L130-L172` — `class CallExpressionValidationAgentOutput(BaseModel):
    """Structured validator-agent summary for one candidate decision run."""

    identity: FrameworkFeatureUsageIdentity
    decision: FrameworkFeatureValidationDecision
    final_confidence: float = Field(ge=0.0, le=1.0)
    target_status: ValidationStatus
    updated_feature_capability_key: str | None = None
    updated_feature_operation_key: str | None = None
    summary: str

    @model_validator(mode="after")
    def validate_decision_contract(self) -> CallExpressionValidationAgentOutput:
        if self.decision == FrameworkFeatureValidationDecision.CORRECT:
            if not self.updated_feature_capability_key:
                raise ValueError(
                    "updated_feature_capability_key is required when decision='correct'"
                )
            if not self.updated_feature_operation_key:
                raise ValueError(
                    "updated_feature_operation_key is required when decision='correct'"
                )
            if (
                self.updated_feature_capability_key
                == self.identity.feature_capability_key
                and self.updated_feature_operation_key
                == self.identity.feature_operation_key
            ):
                raise ValueError(
                    "Updated structured feature identity must differ from identity fields"
                )

        if self.decision == FrameworkFeatureValidationDecision.NEEDS_REVIEW:
            if self.target_status != ValidationStatus.NEEDS_REVIEW:
                raise ValueError(
                    "target_status must be 'needs_review' when decision='needs_review'"
                )
        elif self.target_status != ValidationStatus.COMPLETED:
            raise ValueError(
                "target_status must be 'completed' for confirm/reject/correct decisions"
            )

        return self`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/repository_ruleset_metadata.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/repository_ruleset_metadata.py#L6-L30` — `class CodebaseMetadata(BaseModel):
    codebase_name: str = Field(
        description="The name/identifier of the codebase (relative path from repository root)"
    )
    codebase_path: str = Field(
        description="The absolute file system path to the codebase root directory"
    )
    codebase_programming_language: str = Field(
        description="The programming language of the codebase"
    )
    codebase_package_manager: str = Field(
        description="The package manager of the codebase"
    )
    codebase_package_manager_provenance: Optional[str] = Field(
        default=None,
        description="How the package manager was determined: 'local' or 'inherited'",
    )
    codebase_workspace_root: Optional[str] = Field(
        default=None,
        description="Repo-relative path to nearest workspace/aggregator root",
    )
    codebase_workspace_root_path: Optional[str] = Field(
        default=None,
        description="Absolute filesystem path to workspace/aggregator root",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/repository_ruleset_metadata.py#L33-L39` — `class RepositoryRulesetMetadata(BaseModel):
    repository_qualified_name: str = Field(
        description="The qualified name of the repository"
    )
    codebase_metadata: list[CodebaseMetadata] = Field(
        description="The metadata of the codebases"
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/runtime/agent_dependencies.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/runtime/agent_dependencies.py#L13-L24` — `AgentDependencies`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/runtime/dependency_guide_target.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/runtime/dependency_guide_target.py#L6-L19` — `class DependencyGuideTarget(BaseModel):
    """Canonical dependency documentation target used before agent fan-out."""

    name: str = Field(..., description="Canonical dependency or family name")
    source_packages: list[str] = Field(
        default_factory=list,
        description="Raw package names represented by this documentation target",
    )
    search_query: str | None = Field(
        default=None,
        description="Optional official-doc search query hint for the dependency agent",
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/runtime/dependency_guide_target.py#L22-L28` — `class UIDependencyFamilyMatchRule(BaseModel):
    """Single matcher rule for a configured UI component library family."""

    type: str = Field(..., description="Matcher type: exact, prefix, or regex")
    value: str = Field(..., description="Matcher value for the dependency name")

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/runtime/dependency_guide_target.py#L31-L54` — `class UIDependencyFamilyRule(BaseModel):
    """Configured UI component library family that can collapse many packages."""

    id: str = Field(..., description="Stable unique identifier for the family rule")
    kind: str = Field(..., description="Family kind; currently ui_component_library")
    enabled: bool = Field(default=True, description="Whether the family rule is active")
    languages: list[str] = Field(
        default_factory=list,
        description="Optional programming language filter for this family rule",
    )
    package_managers: list[str] = Field(
        default_factory=list,
        description="Optional package-manager filter for this family rule",
    )
    display_name: str = Field(..., description="Canonical name to document")
    search_query: str | None = Field(
        default=None,
        description="Optional official-doc search query override",
    )
    match: UIDependencyFamilyMatchRule = Field(
        ..., description="Rule used to match raw dependency package names"
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/runtime/dependency_guide_target.py#L57-L66` — `class UIDependencyFamilyRegistry(BaseModel):
    """Registry of explicitly configured UI component library families."""

    version: int = Field(..., description="Registry schema version")
    families: list[UIDependencyFamilyRule] = Field(
        default_factory=list,
        description="Configured UI component library family rules",
    )

    model_config = ConfigDict(extra="forbid")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/statistics/agent_usage_statistics.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/statistics/agent_usage_statistics.py#L8-L45` — `class UsageStatistics(BaseModel):
    """Statistics for tracking LLM usage and costs.

    Used for per-codebase aggregation.
    """

    requests: int = Field(
        default=0,
        description="Number of requests made to the LLM API",
    )
    tool_calls: int = Field(
        default=0,
        description="Number of successful tool calls executed",
    )
    input_tokens: int = Field(
        default=0,
        description="Total number of input/prompt tokens",
    )
    output_tokens: int = Field(
        default=0,
        description="Total number of output/completion tokens",
    )
    cache_write_tokens: int = Field(
        default=0,
        description="Total number of tokens written to cache",
    )
    cache_read_tokens: int = Field(
        default=0,
        description="Total number of tokens read from cache",
    )
    total_tokens: int = Field(
        default=0,
        description="Total tokens (input + output)",
    )
    estimated_cost_usd: Optional[float] = Field(
        default=None,
        description="Estimated cost in USD (requires gen-ai-prices integration)",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/statistics/agent_usage_statistics.py#L48-L62` — `class UsageSummary(BaseModel):
    """Temporary aggregation helper for combining usage and cost.

    Used during agent execution to track both usage metrics and cost
    before final aggregation into WorkflowStatistics.
    """

    usage: Dict[str, Any] = Field(
        default_factory=dict,
        description="RunUsage fields as dict (requests, tool_calls, tokens, etc., including nested 'details')",
    )
    cost_usd: Optional[float] = Field(
        default=None,
        description="Estimated cost in USD for this execution",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/statistics/agent_usage_statistics.py#L65-L103` — `class WorkflowStatistics(BaseModel):
    """Complete workflow statistics aggregated across all codebases."""

    total_requests: int = Field(
        default=0,
        description="Total number of requests across all codebases",
    )
    total_tool_calls: int = Field(
        default=0,
        description="Total number of tool calls across all codebases",
    )
    total_input_tokens: int = Field(
        default=0,
        description="Total input tokens across all codebases",
    )
    total_output_tokens: int = Field(
        default=0,
        description="Total output tokens across all codebases",
    )
    total_cache_write_tokens: int = Field(
        default=0,
        description="Total cache write tokens",
    )
    total_cache_read_tokens: int = Field(
        default=0,
        description="Total cache read tokens",
    )
    total_tokens: int = Field(
        default=0,
        description="Total tokens (input + output) across all processing",
    )
    total_estimated_cost_usd: Optional[float] = Field(
        default=None,
        description="Total estimated cost in USD for the entire workflow",
    )
    by_codebase: Dict[str, UsageStatistics] = Field(
        default_factory=dict,
        description="Statistics broken down by codebase name",
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py#L31-L37` — `TokenResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py#L41-L46` — `CodexAuthContext`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py#L50-L56` — `CodexOAuthStatus`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py#L60-L70` — `CodexOAuthFlow`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/provider_catalog.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/provider_catalog.py#L8-L18` — `class ProviderField(BaseModel):
    """Schema for a provider configuration field."""

    key: str
    label: str
    type: str  # text, password, select, number, boolean, url
    required: bool = False
    default: Any = None
    placeholder: Optional[str] = None
    help: Optional[str] = None
    enum: Optional[List[str]] = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/provider_catalog.py#L21-L38` — `class ProviderSchema(BaseModel):
    """Schema for a provider's configuration."""

    provider_key: str
    display_name: str
    kind: str  # native | openai_compat
    model_field: Dict[str, Any]
    fields: List[ProviderField]

    def to_public(self) -> "ProviderSchemaPublic":
        """Return a variant without the redundant provider_key field."""

        return ProviderSchemaPublic(
            display_name=self.display_name,
            kind=self.kind,
            model_field=self.model_field,
            fields=self.fields,
        )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/provider_catalog.py#L41-L47` — `class ProviderSchemaPublic(BaseModel):
    """Public-facing provider schema shape without provider_key for API responses."""

    display_name: str
    kind: str
    model_field: Dict[str, Any]
    fields: List[ProviderField]`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/activity_policies.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/activity_policies.py#L15-L21` — `TemporalActivityDefaults`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/activity_policies.py#L25-L43` — `ResolvedTemporalActivityConfig`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/runtime.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/runtime.py#L24-L31` — `AgentAssemblyContext`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/runtime.py#L35-L40` — `AgentBuildResult`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/search.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/search.py#L22-L28` — `SearchRuntimePolicy`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py#L44-L82` — `class TemporalAgentRegistry(BaseModel):
    """Precise registry model for enabled Temporal agents."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    development_workflow_guide: (
        TemporalAgent[AgentDependencies, EngineeringWorkflow] | None
    ) = None
    dependency_guide: TemporalAgent[AgentDependencies, DependencyGuideEntry] | None = (
        None
    )
    business_domain_guide: TemporalAgent[AgentDependencies, str] | None = None
    agents_md_updater: TemporalAgent[AgentDependencies, AgentsMdUpdaterOutput] | None = (
        None
    )
    call_expression_validator: (
        TemporalAgent[AgentDependencies, CallExpressionValidationAgentOutput] | None
    ) = None

    def iter_agents(self) -> Iterator[TemporalAgent[AgentDependencies, Any]]:
        """Yield all enabled temporal agents."""
        for field_name in type(self).model_fields:
            agent = getattr(self, field_name)
            if agent is not None:
                yield agent

    def iter_agent_names(self) -> Iterator[str]:
        """Yield field names for all enabled temporal agents."""
        for field_name in type(self).model_fields:
            if getattr(self, field_name) is not None:
                yield field_name

    def enabled_agent_names(self) -> list[str]:
        """Return enabled temporal agent names in declaration order."""
        return list(self.iter_agent_names())

    def enabled_agent_count(self) -> int:
        """Return the number of enabled temporal agents."""
        return len(self.enabled_agent_names())`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/workflow_envelopes.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/workflow_envelopes.py#L13-L36` — `class AgentSnapshotCompleteEnvelope(BaseModel):
    """Envelope for persisting agent snapshot completion to database.

    Used by RepositoryAgentSnapshotActivity to call complete_run()
    and persist final agent_md_output and statistics.
    """

    owner_name: str = Field(..., description="Repository owner name")
    repo_name: str = Field(..., description="Repository name")
    repository_workflow_run_id: str = Field(
        ..., description="Workflow run ID for correct row targeting"
    )
    final_payload: dict[str, Any] = Field(
        ..., description="Final agent MD output payload to persist"
    )
    statistics_payload: Optional[dict[str, Any]] = Field(
        default=None, description="Usage statistics (optional, added by task-013)"
    )
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        """Return any extra fields passed to the model (required for Temporal)."""
        return dict(self.model_extra or {})`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/tools/agents_md_updater_tools.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/tools/agents_md_updater_tools.py#L23-L28` — `ReplacementChunk`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/tools/agents_md_updater_tools.py#L32-L38` — `PatchOperation`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/tools/search_across_codebase.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/tools/search_across_codebase.py#L25-L37` — `class SearchMatch(BaseModel):
    """Represents a single search match with contextual information."""

    file_path: str = Field(..., description="Path relative to the codebase root")
    line: int = Field(..., description="1-based line number of the match")
    text: str = Field(..., description="The line content containing the match")
    preview: Optional[str] = Field(
        None,
        description=(
            "Optional multi-line preview including up to `context` lines "
            "before and after the match. The matched line is included in the preview."
        ),
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/tools/search_across_codebase.py#L40-L52` — `class SearchResults(BaseModel):
    """Container for search results with metadata."""

    pattern: str = Field(..., description="The search pattern used")
    matches: List[SearchMatch] = Field(
        default_factory=list, description="Matches, capped by max_results"
    )
    total: int = Field(
        ..., description="Total number of matches found across all files"
    )
    truncated: bool = Field(
        ..., description="True if results were capped by max_results"
    )`
