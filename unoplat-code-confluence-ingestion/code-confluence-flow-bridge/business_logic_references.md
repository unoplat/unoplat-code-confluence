# Business Logic References

## Domain Summary
This codebase is centered on GitHub repository ingestion and codebase analysis for Code Confluence, modeling repositories, codebases, files, imports, structural signatures, and package-manager metadata across Python and TypeScript. It also manages workflow state for ingestion, agent-generation, and markdown-update jobs, including progress, errors, issue tracking, and feedback handling. A secondary slice handles GitHub App manifest onboarding and repository/provider metadata used to register and refresh ingested repositories.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_source_context.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_source_context.py#L149-L176` — `class PythonSourceContext(BaseModel):
    """Shared parsed source context for Python detection paths."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_code: str
    source_bytes: bytes
    tree: tree_sitter.Tree
    root_node: tree_sitter.Node
    imports: List[str]
    import_aliases: Dict[str, str]

    @classmethod
    def from_source(cls, source_code: str) -> "PythonSourceContext":
        source_bytes = source_code.encode("utf-8", errors="ignore")
        parser = get_parser("python")
        tree = parser.parse(source_bytes)
        root_node = tree.root_node
        imports = _extract_imports_from_tree(root_node, source_bytes)
        import_aliases = build_import_aliases(imports)
        return cls(
            source_code=source_code,
            source_bytes=source_bytes,
            tree=tree,
            root_node=root_node,
            imports=imports,
            import_aliases=import_aliases,
        )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py#L72-L86` — `CallMatchEvidence`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_source_context.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_source_context.py#L153-L189` — `class TypeScriptSourceContext(BaseModel):
    """Shared parsed source context for TypeScript detection paths."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_code: str
    source_bytes: bytes
    tree: tree_sitter.Tree
    root_node: tree_sitter.Node
    imports: List[str]
    import_aliases: Dict[str, str]

    @classmethod
    def from_source(cls, source_code: str) -> "TypeScriptSourceContext":
        """Parse TypeScript source and build a fully-populated context.

        Args:
            source_code: Raw TypeScript source text.

        Returns:
            A ``TypeScriptSourceContext`` with the parse tree, extracted
            imports, and resolved import-alias mapping ready for detection.
        """
        source_bytes = source_code.encode("utf-8", errors="ignore")
        parser = get_parser("typescript")  # type: ignore[arg-type]
        tree = parser.parse(source_bytes)
        root_node = tree.root_node
        imports = _extract_imports_from_tree(root_node, source_bytes)
        import_aliases = build_import_aliases(imports)
        return cls(
            source_code=source_code,
            source_bytes=source_bytes,
            tree=tree,
            root_node=root_node,
            imports=imports,
            import_aliases=import_aliases,
        )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py#L72-L85` — `CallMatchEvidence`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L18-L38` — `class GithubAppManifestRecord(SQLBase):
    """Database record tracking active manifest states awaiting conversion."""

    __tablename__ = "github_app_manifest_request"
    __table_args__ = (
        Index(
            "ix_github_app_manifest_request_expires_at",
            "expires_at",
        ),
    )

    state: Mapped[str] = mapped_column(primary_key=True)
    manifest_json: Mapped[str] = mapped_column(Text, nullable=False)
    owner_login: Mapped[Optional[str]] = mapped_column(nullable=True)
    owner_type: Mapped[str] = mapped_column(nullable=False, default="user")
    registration_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    requested_by: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L41-L81` — `class ManifestGenerationRequest(BaseModel):
    """Incoming payload for initiating the manifest flow."""

    owner: Optional[str] = Field(
        default=None,
        description=(
            "GitHub username or organization slug that will own the GitHub App. "
            "Falls back to service defaults when omitted."
        ),
    )
    owner_type: Literal["user", "organization"] = Field(
        default="user",
        description="Determines whether to use /settings/apps/new or /organizations/{owner}/settings/apps/new.",
    )
    service_base_url: AnyHttpUrl = Field(
        description="Base URL where this service is reachable (e.g. https://bridge.example.com).",
    )
    webhook_proxy_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Optional webhook proxy (e.g. smee.io) used in place of the service webhook for local testing.",
    )
    app_name: Optional[str] = Field(
        default=None,
        description="Optional override for the GitHub App name; defaults to the service configuration.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional override for the GitHub App description.",
    )
    homepage_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Optional override for the GitHub App homepage URL.",
    )
    post_install_redirect_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Optional URL GitHub should redirect to after the installation completes.",
    )
    requested_by: Optional[str] = Field(
        default=None,
        description="Opaque identifier representing the operator that initiated the manifest flow.",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L84-L105` — `class ManifestGenerationResponse(BaseModel):
    """Response payload returned to the operator initiating the manifest flow."""

    state: str = Field(
        description="Opaque state token that must be echoed back by GitHub."
    )
    manifest: Dict[str, Any] = Field(
        description="Final manifest JSON submitted to GitHub."
    )
    registration_url: AnyHttpUrl = Field(
        description="GitHub URL the operator should open to register the manifest."
    )
    owner: Optional[str] = Field(
        default=None, description="Effective owner slug resolved for the manifest."
    )
    owner_type: Literal["user", "organization"] = Field(
        description="Owner type that will receive the GitHub App."
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp (UTC) when the manifest state will expire if unused.",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L108-L122` — `class ManifestConversionResponse(BaseModel):
    """Response payload returned after exchanging the manifest code with GitHub."""

    app_slug: str = Field(description="Short slug assigned to the created GitHub App.")
    app_id: int = Field(description="Numeric identifier of the created GitHub App.")
    client_id: str = Field(
        description="OAuth client identifier associated with the app."
    )
    html_url: AnyHttpUrl = Field(description="GitHub UI URL for managing the app.")
    installation_url: AnyHttpUrl = Field(
        description="URL the operator should visit to install the GitHub App."
    )
    instructions: List[str] = Field(
        description="Ordered list of recommended follow-up steps for the operator."
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/file_processing_data.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/file_processing_data.py#L8-L19` — `class FileProcessingData(BaseModel):
    """Data structure for file processing with structural signature."""

    file_path: str = Field(description="Absolute path to the source file")
    content: str = Field(description="Full content of the file")
    checksum: str = Field(description="MD5 checksum of the file content")
    structural_signature: Dict = Field(description="AST-level structural signature")
    imports: List[str] = Field(description="List of import statements in the file")
    poi_labels: List[str] = Field(description="Points of interest labels for the file")
    package_qualified_name: str = Field(
        description="Qualified name of the containing package"
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/import_info.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/import_info.py#L8-L13` — `class ImportInfo(BaseModel):
    """Information about import statements in a file."""

    start_line: int = Field(..., description="Starting line number of import block")
    end_line: int = Field(..., description="Ending line number of import block")
    imports: List[str] = Field(..., description="Array of import statement strings")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/position.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/position.py#L8-L12` — `class Position(BaseModel):
    """Represents source code location information."""

    start_line: Optional[int] = Field(default=None, alias="StartLine")
    stop_line: Optional[int] = Field(default=None, alias="StopLine")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/processing_batch.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/processing_batch.py#L12-L18` — `class ProcessingBatch(BaseModel):
    """Represents a batch of files for processing."""

    batch_id: str = Field(description="Unique identifier for the batch")
    files: List[FileProcessingData] = Field(description="List of files in this batch")
    total_files: int = Field(description="Total number of files in the batch")
    batch_size: int = Field(description="Maximum number of files per batch")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_codebase.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_codebase.py#L15-L35` — `class UnoplatCodebase(BaseModel):
    """Represents a single codebase within a repository."""

    name: str = Field(description="Name of the codebase usually the root package name")
    readme: Optional[str] = Field(default=None, description="Optional codebase README")
    packages: Optional[UnoplatPackage] = Field(
        default=None, description="The root package of the codebase"
    )
    package_manager_metadata: UnoplatPackageManagerMetadata = Field(
        description="The package manager metadata of the codebase"
    )
    root_packages: List[str] = Field(
        description="List of root package paths within the codebase"
    )
    codebase_path: str = Field(description="Codebase root directory path (absolute)")
    codebase_folder: str = Field(
        description="Codebase folder path relative to repository root"
    )
    programming_language: Optional[Literal["python", "java", "go", "typescript"]] = (
        Field(default=None, description="Programming language of the codebase")
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_file.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_file.py#L14-L41` — `class UnoplatFile(BaseModel):
    """Represents individual source code files."""

    file_path: str = Field(description="Absolute file path")
    checksum: Optional[str] = Field(
        default=None, description="Optional content checksum for change tracking"
    )
    structural_signature: Optional[
        Union[PythonStructuralSignature, TypeScriptStructuralSignature]
    ] = Field(
        default=None,
        description="Language-specific structural signature capturing the high-level outline of the file",
    )
    imports: Optional[List[str]] = Field(
        default_factory=list, description="List of imports in the file"
    )
    custom_features_list: Optional[List[Detection]] = Field(
        default=None, description="List of custom features detected in the file"
    )
    has_data_model: bool = Field(
        default=False,
        description="True if file contains classes that are data models (e.g., @dataclass)",
    )

    data_model_positions: DataModelPosition = Field(
        default_factory=DataModelPosition,
        description="Positions of data models detected in the file",
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_git_repository.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_git_repository.py#L12-L37` — `class UnoplatGitRepository(BaseModel):
    """
    Represents the top-level Git repository containing multiple codebases.

    TODO: Currently this is the root. Moving forward, root should be an Organisation
    and then it should have multiple Domains. And then each domain should have
    multiple repositories.
    """

    repository_url: str = Field(description="The URL of the repository")
    repository_name: str = Field(description="The name of the repository")
    repository_metadata: Dict[str, Any] = Field(
        description="The metadata of the repository"
    )
    codebases: List[UnoplatCodebase] = Field(
        default_factory=list, description="The codebases of the repository"
    )
    readme: Optional[str] = Field(
        default=None, description="The readme of the repository"
    )
    domain: Optional[str] = Field(
        default=None, description="The domain of the repository"
    )
    github_organization: Optional[str] = Field(
        default=None, description="The github organization of the repository"
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package.py#L12-L22` — `class UnoplatPackage(BaseModel):
    """Represents a package/module in the codebase with hierarchical structure."""

    name: Optional[str] = Field(default=None, description="Name of the package")
    files: Dict[str, UnoplatFile] = Field(
        default_factory=dict, description="Dict of file paths to file objects"
    )
    sub_packages: Optional[Dict[str, "UnoplatPackage"]] = Field(
        default_factory=lambda: {},
        description="Dict of the sub-packages for the package",
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package_manager_metadata.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package_manager_metadata.py#L12-L100` — `class UnoplatPackageManagerMetadata(BaseModel):
    """Comprehensive package manager and project metadata."""

    dependencies: Dict[str, Dict[str, UnoplatProjectDependency]] = Field(
        default_factory=dict,
        description="Dependency groups keyed by group name then package name",
    )
    package_name: Optional[str] = Field(
        default=None, description="The name of the package"
    )
    programming_language: str = Field(
        description="The programming language of the project"
    )
    package_manager: str = Field(description="The package manager of the project")
    programming_language_version: Optional[str] = Field(
        default=None, description="The version of the programming language"
    )
    project_version: Optional[str] = Field(
        default=None, description="The version of the project"
    )
    description: Optional[str] = Field(
        default=None, description="The description of the project"
    )
    authors: Optional[List[str]] = Field(
        default=None, description="The authors of the project"
    )
    license: Optional[Dict[str, Any]] = Field(
        default=None, description="The license of the project"
    )
    entry_points: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary of script names to their entry points. Example: {'cli': 'package.module:main', 'serve': 'uvicorn app:main'}",
    )
    scripts: Dict[str, str] = Field(
        default_factory=dict,
        description="Lifecycle commands from package manifests (e.g., npm scripts)",
    )
    binaries: Dict[str, str] = Field(
        default_factory=dict,
        description="Command-to-executable mappings declared via bin/exports for CLI usage",
    )
    # New fields for additional metadata
    homepage: Optional[str] = Field(
        default=None, description="The homepage URL of the project"
    )
    repository: Optional[str] = Field(
        default=None, description="The repository URL of the project"
    )
    documentation: Optional[str] = Field(
        default=None, description="The documentation URL of the project"
    )
    keywords: List[str] = Field(
        default_factory=list, description="List of keywords/tags for the project"
    )
    maintainers: List[str] = Field(
        default_factory=list, description="List of project maintainers"
    )
    readme: Optional[str] = Field(
        default=None, description="Path to or content of the project's README file"
    )
    manifest_path: Optional[str] = Field(
        default=None,
        description="Path to the package manifest relative to repository root",
    )

    @field_validator("license", mode="before")
    @classmethod
    def validate_license(cls, value: Any) -> Optional[Dict[str, Any]]:
        """Validate and normalize license field which can be a string or a dict.

        Args:
            value: License value which can be a string like "MIT" or a dict like {"text": "MIT License"}

        Returns:
            Normalized license dictionary or None if not provided
        """
        if value is None:
            return None

        # If it's already a dict, return it as is
        if isinstance(value, dict):
            return value

        # If it's a string, convert it to a dict with 'text' key
        if isinstance(value, str):
            return {"text": value}

        # For any other type, convert to string and store as 'text'
        return {"text": str(value)}`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_project_dependency.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_project_dependency.py#L12-L36` — `class UnoplatProjectDependency(BaseModel):
    """Represents individual project dependencies with detailed constraints."""

    version: UnoplatVersion = Field(
        default_factory=UnoplatVersion, description="Version constraint"
    )
    extras: Optional[List[str]] = Field(
        default=None, description="List of extras for this dependency"
    )
    source: Optional[str] = Field(
        default=None, description="Source of the dependency (e.g. 'git', 'url', 'path')"
    )
    source_url: Optional[str] = Field(
        default=None, description="URL or path to the dependency source"
    )
    source_reference: Optional[str] = Field(
        default=None, description="Branch, tag, or commit reference"
    )
    subdirectory: Optional[str] = Field(
        default=None, description="Subdirectory within source"
    )
    environment_marker: Optional[str] = Field(
        default=None,
        description="PEP 508 environment marker string (e.g., python_version < '3.7')",
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_version.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_version.py#L8-L22` — `class UnoplatVersion(BaseModel):
    """Flexible version constraint representation."""

    specifier: Optional[str] = Field(
        default=None, description="Version specifier string (e.g., '>=1.0.0,<2.0.0')"
    )
    minimum_version: Optional[str] = Field(
        default=None, description="Minimum allowed version"
    )
    maximum_version: Optional[str] = Field(
        default=None, description="Maximum allowed version"
    )
    current_version: Optional[str] = Field(
        default=None, description="Currently installed/used version"
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/configuration/settings.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/configuration/settings.py#L13-L15` — `class LLMProviderConfig(BaseModel):
    llm_model_provider: str
    llm_model_provider_args: Dict[str, Any]`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py#L6-L12` — `class RuleSignatureConfig(BaseModel):
    """Typed YAML representation for a manager signature entry."""

    file: str | None = None
    contains: str | None = None
    contains_absence: list[str] | None = None
    glob: str | None = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py#L15-L21` — `class RuleManagerConfig(BaseModel):
    """Typed YAML representation for a manager entry."""

    manager: str
    weight: int = 1
    signatures: list[str | RuleSignatureConfig] = Field(default_factory=list)
    workspace_field: str | None = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py#L24-L28` — `class LanguageRulesConfig(BaseModel):
    """Typed YAML representation for the Python rules block."""

    ignores: list[str] = Field(default_factory=list)
    managers: list[RuleManagerConfig] = Field(default_factory=list)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py#L31-L34` — `class RulesFileConfig(BaseModel):
    """Typed YAML representation for the full rules file (Python section)."""

    python: LanguageRulesConfig = Field(default_factory=LanguageRulesConfig)`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/evidence.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/evidence.py#L6-L13` — `class ManagerDetectionResult(BaseModel):
    """Structured package-manager detection evidence."""

    model_config = ConfigDict(frozen=True)

    manager_name: str = Field(description="Detected package manager name.")
    evidence_type: str = Field(description="Type of evidence that matched the manager.")
    evidence_value: str = Field(description="Matched filename, glob, or field name.")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/inventory.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/inventory.py#L10-L15` — `class FileNode(BaseModel):
    """A single path from the repository inventory."""

    path: str  # e.g. "src/foo/__init__.py"
    kind: Literal["file", "dir"]
    size: Optional[int] = None  # bytes (None for directories)`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/results.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/results.py#L10-L33` — `class DetectedCodebase(BaseModel):
    """Detection result carrying package-manager provenance and workspace context."""

    manager_name: str = Field(
        description="Effective package manager name (e.g. 'bun', 'pnpm', 'npm', 'yarn')"
    )
    provenance: PackageManagerProvenance = Field(
        description="Whether the package manager was detected locally or inherited from a parent workspace"
    )
    workspace_root: str | None = Field(
        default=None,
        description=(
            "Repo-relative POSIX path to the nearest aggregator directory "
            "that owns workspace commands. None for standalone or locally-owned leaf codebases."
        ),
    )
    workspace_orchestrator: WorkspaceOrchestratorType | None = Field(
        default=None,
        description="Nearest authoritative workspace orchestrator for workflow discovery.",
    )
    workspace_orchestrator_config_path: str | None = Field(
        default=None,
        description="Repo-relative config path for the nearest authoritative workspace orchestrator.",
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/rules.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/rules.py#L10-L21` — `class Signature(BaseModel):
    """
    A test applied to the set of filenames in a directory, or to the file
    contents if 'contains' is supplied.
    """

    file: Optional[str] = None  # exact filename to look for
    contains: Optional[str] = None  # substring that must appear in that file
    contains_absence: Optional[List[str]] = (
        None  # substrings that must NOT appear in file
    )
    glob: Optional[str] = None  # shell-style wildcard pattern`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/rules.py#L24-L32` — `class ManagerRule(BaseModel):
    """Package manager detection rule."""

    manager: str  # "poetry", "pip", "maven", …
    weight: int = 1  # for tie-breaking / confidence
    signatures: List[Signature] = Field(default_factory=list)
    workspace_field: Optional[str] = (
        None  # e.g. "workspaces" for npm, "tool.uv.workspace" for uv
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/rules.py#L35-L39` — `class LanguageRules(BaseModel):
    """Language-specific detection rules."""

    ignores: List[str]  # dir tokens to drop if not referenced
    managers: List[ManagerRule]`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/discovery.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/discovery.py#L11-L21` — `class WorkspaceOrchestratorMetadata(BaseModel):
    """Authoritative workspace-runner metadata attached to a workspace root."""

    model_config = ConfigDict(frozen=True)

    orchestrator: WorkspaceOrchestratorType = Field(
        description="Nearest authoritative monorepo orchestrator."
    )
    config_path: str = Field(
        description="Repo-relative path to the authoritative orchestrator config file."
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/discovery.py#L24-L42` — `class WorkspaceDiscoveryContext(BaseModel):
    """Authoritative workspace membership and ownership resolved from root config."""

    model_config = ConfigDict(frozen=True)

    root_dir: str = Field(description="Repo-relative directory owning the workspace.")
    manager_name: str = Field(description="Package manager owning the workspace root.")
    member_dirs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Repo-relative workspace member directories.",
    )
    excluded_dirs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Repo-relative directories excluded by workspace negations.",
    )
    orchestrator: WorkspaceOrchestratorMetadata | None = Field(
        default=None,
        description="Nearest authoritative workspace orchestrator metadata.",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/discovery.py#L45-L69` — `class TypeScriptRepositoryScan(BaseModel):
    """Single ripgrep-backed repository scan reused across detector phases."""

    model_config = ConfigDict(frozen=True)

    inventory: tuple[FileNode, ...] = Field(
        default_factory=tuple,
        description="Repository file inventory captured from ripgrep.",
    )
    inventory_paths: frozenset[str] = Field(
        default_factory=frozenset,
        description="Fast lookup set of repo-relative inventory paths.",
    )
    dirs_to_files: dict[str, tuple[str, ...]] = Field(
        default_factory=dict,
        description="Repo-relative directory to matching file paths.",
    )
    known_dirs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Known repo-relative directories discovered during the scan.",
    )
    manifest_dirs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Repo-relative directories that contain a package.json manifest.",
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L6-L12` — `class RuleSignatureConfig(BaseModel):
    """Typed YAML representation for a manager signature entry."""

    file: str | None = None
    contains: str | None = None
    contains_absence: list[str] | None = None
    glob: str | None = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L15-L21` — `class RuleManagerConfig(BaseModel):
    """Typed YAML representation for a manager entry."""

    manager: str
    weight: int = 1
    signatures: list[str | RuleSignatureConfig] = Field(default_factory=list)
    workspace_field: str | None = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L24-L28` — `class LanguageRulesConfig(BaseModel):
    """Typed YAML representation for the TypeScript rules block."""

    ignores: list[str] = Field(default_factory=list)
    managers: list[RuleManagerConfig] = Field(default_factory=list)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L31-L34` — `class RulesFileConfig(BaseModel):
    """Typed YAML representation for the full rules file."""

    typescript: LanguageRulesConfig = Field(default_factory=LanguageRulesConfig)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L37-L40` — `class WorkspacePackagesConfig(BaseModel):
    """Typed object-form `package.json.workspaces` config."""

    packages: list[str] = Field(default_factory=list)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L43-L46` — `class PnpmWorkspaceConfig(BaseModel):
    """Typed `pnpm-workspace.yaml` config."""

    packages: list[str] = Field(default_factory=list)`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L15-L25` — `class GitHubOwner(BaseModel):
    """GitHub repository owner model."""

    login: str = Field(description="The username of the owner")
    id: int = Field(description="Unique identifier of the owner")
    node_id: str = Field(description="Node ID of the owner")
    avatar_url: str = Field(description="URL to the owner's avatar")
    html_url: str = Field(description="HTML URL of the owner")
    type: str = Field(description="Type of the owner (User, Organization)")
    site_admin: bool = Field(description="Whether the owner is a site admin")
    url: str = Field(description="API URL of the owner")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L28-L35` — `class GitHubLicense(BaseModel):
    """GitHub repository license model."""

    key: str = Field(description="License key")
    name: str = Field(description="License name")
    url: Optional[str] = Field(default=None, description="License URL")
    spdx_id: Optional[str] = Field(default=None, description="SPDX ID of the license")
    node_id: str = Field(description="Node ID of the license")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L38-L84` — `class GitHubRepo(BaseModel):
    """Model for GitHub repository data based on GitHub API response."""

    id: int = Field(description="Unique identifier of the repository")
    node_id: str = Field(description="Node ID of the repository")
    name: str = Field(description="The name of the repository")
    full_name: str = Field(description="Full name of the repository (owner/repo)")
    private: bool = Field(description="Whether the repository is private")
    owner: GitHubOwner = Field(description="Owner of the repository")
    html_url: str = Field(description="HTML URL of the repository")
    description: Optional[str] = Field(
        default=None, description="Repository description"
    )
    fork: bool = Field(description="Whether the repository is a fork")
    url: str = Field(description="API URL of the repository")
    git_url: str = Field(description="Git URL of the repository")
    ssh_url: str = Field(description="SSH URL of the repository")
    clone_url: str = Field(description="Clone URL of the repository")
    default_branch: str = Field(description="Default branch of the repository")
    created_at: Optional[str] = Field(
        default=None, description="Repository creation date"
    )
    updated_at: Optional[str] = Field(
        default=None, description="Repository last update date"
    )
    pushed_at: Optional[str] = Field(default=None, description="Last push date")
    language: Optional[str] = Field(
        default=None, description="Primary language of the repository"
    )
    license: Optional[GitHubLicense] = Field(
        default=None, description="Repository license"
    )
    forks_count: int = Field(description="Number of forks")
    stargazers_count: int = Field(description="Number of stars")
    watchers_count: int = Field(description="Number of watchers")
    size: int = Field(description="Size of the repository in KB")
    open_issues_count: int = Field(description="Number of open issues")
    topics: Optional[List[str]] = Field(default=None, description="Repository topics")
    has_issues: bool = Field(description="Whether issues are enabled")
    has_projects: bool = Field(description="Whether projects are enabled")
    has_wiki: bool = Field(description="Whether the wiki is enabled")
    has_pages: bool = Field(description="Whether GitHub Pages is enabled")
    archived: bool = Field(description="Whether the repository is archived")
    disabled: bool = Field(description="Whether the repository is disabled")
    visibility: Optional[str] = Field(
        default=None, description="Repository visibility (public, private, internal)"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L87-L94` — `class GitHubRepoSummary(BaseModel):
    """Simplified model for GitHub repository data."""

    name: str = Field(description="The name of the repository")
    owner_url: str = Field(description="HTML URL of the repository owner")
    private: bool = Field(description="Whether the repository is private")
    git_url: str = Field(description="Git URL of the repository")
    owner_name: str = Field(description="Login of the repository owner")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L97-L103` — `class PaginatedResponse(BaseModel):
    items: List[GitHubRepoSummary]
    per_page: int = Field(description="Number of items per page")
    has_next: bool = Field(description="Whether there are more items to fetch")
    next_cursor: Optional[str] = Field(
        default=None, description="Cursor for the next page of results"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L111-L126` — `class IssueTracking(BaseModel):
    issue_id: Optional[str] = Field(
        default=None, description="Issue ID associated with the error"
    )
    issue_number: Optional[int] = Field(
        default=None, description="Issue number in the GitHub repository"
    )
    issue_url: Optional[str] = Field(
        default=None, description="Issue URL associated with the error"
    )
    issue_status: Optional[IssueStatus] = Field(
        default=None, description="Issue status associated with the error"
    )
    created_at: Optional[str] = Field(
        default=None, description="Timestamp when the issue was created"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L129-L148` — `class WorkflowRun(BaseModel):
    codebase_workflow_run_id: str = Field(
        description="Unique identifier for this specific run instance of the workflow."
    )
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    status: JobStatus = Field(
        description=(
            "Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, "
            "TIMED_OUT, COMPLETED, RETRYING, ERROR, CANCELLED."
        )
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the workflow run completed"
    )
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error report if the workflow run failed"
    )
    issue_tracking: Optional[IssueTracking] = Field(
        default=None, description="GitHub issue tracking info for the workflow run"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L151-L157` — `class WorkflowStatus(BaseModel):
    codebase_workflow_id: str = Field(
        description="Unique identifier for the workflow (remains constant across execution runs)."
    )
    codebase_workflow_runs: List[WorkflowRun] = Field(
        description="Multiple run instances for this workflow."
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L160-L164` — `class CodebaseStatus(BaseModel):
    codebase_folder: str = Field(description="The folder path of the codebase.")
    workflows: List[WorkflowStatus] = Field(
        description="List of workflows under this codebase."
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L167-L170` — `class CodebaseStatusList(BaseModel):
    codebases: List[CodebaseStatus] = Field(
        description="List of codebases each with multiple workflows."
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L173-L185` — `class RepositoryRequestConfiguration(BaseModel):
    """Configuration for a repository ingestion request, including codebase config and provider credentials."""

    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_git_url: str = Field(description="The git URL of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_metadata: Optional[List[CodebaseConfig]] = Field(
        default=None,
        description="List of codebase configurations for the repository (auto-detected if not provided)",
    )
    provider_key: ProviderKey = Field(
        ..., description="Provider key for credential and repository provider lookup"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L188-L199` — `class RepositoryRefreshRequest(BaseModel):
    """Minimal payload accepted by the refresh endpoint."""

    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_owner_name: str = Field(description="The name of the repository owner")
    provider_key: ProviderKey = Field(
        ..., description="Provider key for credential lookup during refresh"
    )
    repository_git_url: Optional[str] = Field(
        default=None,
        description="Optional git URL override. If omitted, the backend derives it from provider metadata.",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L202-L209` — `class GitHubRepoResponseConfiguration(BaseModel):
    """Configuration for a GitHub repository, including codebase config and status."""

    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_metadata: List[CodebaseConfig] = Field(
        description="List of codebase configurations for the repository"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L212-L230` — `class CodebaseCurrentStatus(BaseModel):
    """Model for current status of a single codebase workflow run."""

    codebase_folder: str = Field(description="The folder path of the codebase")
    codebase_workflow_run_id: str = Field(
        description="The run ID of the codebase workflow"
    )
    codebase_workflow_id: str = Field(description="The ID of the codebase workflow")
    status: JobStatus = Field(description="Status of the workflow run")
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    completed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the workflow run completed"
    )
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error report if the workflow run failed"
    )
    issue_tracking: Optional[IssueTracking] = Field(
        default=None, description="GitHub issue tracking info for the workflow run"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L233-L262` — `class GithubRepoStatus(BaseModel):
    """Model for current status of a repository workflow run and its associated codebase runs."""

    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_workflow_run_id: str = Field(
        description="The run ID of the repository workflow"
    )
    repository_workflow_id: str = Field(description="The ID of the repository workflow")
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    status: JobStatus = Field(
        description=(
            "Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, "
            "TIMED_OUT, COMPLETED, RETRYING, ERROR, CANCELLED."
        )
    )
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error report if the workflow run failed"
    )
    issue_tracking: Optional[IssueTracking] = Field(
        default=None,
        description="GitHub issue tracking info for the repository workflow run",
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the workflow run completed"
    )
    codebase_status_list: Optional[CodebaseStatusList] = Field(
        default=None,
        description="Status of the repository workflows (optional, returned in GET)",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L265-L296` — `class ParentWorkflowJobResponse(BaseModel):
    """Response model for parent workflow job data API."""

    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_workflow_run_id: str = Field(
        description="The run ID of the repository workflow"
    )
    operation: RepositoryWorkflowOperation = Field(
        description="Operation type of the workflow run. One of: INGESTION, AGENTS_GENERATION, AGENT_MD_UPDATE."
    )
    status: JobStatus = Field(
        description=(
            "Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, "
            "TIMED_OUT, COMPLETED, RETRYING, ERROR, CANCELLED."
        )
    )
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    completed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the workflow run completed"
    )
    feedback_issue_url: Optional[str] = Field(
        default=None,
        description="URL of the GitHub issue created from agent feedback submission",
    )
    is_cancellable: bool = Field(
        default=False,
        description=(
            "Whether this workflow run can be canceled by users from the operations "
            "management UI"
        ),
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L299-L304` — `class ParentWorkflowJobListResponse(BaseModel):
    """Response model containing a list of parent workflow job data."""

    jobs: List[ParentWorkflowJobResponse] = Field(
        description="List of parent workflow jobs"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L312-L326` — `class GithubIssueSubmissionRequest(BaseModel):
    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    parent_workflow_run_id: str = Field(description="The run ID of the parent workflow")
    error_type: IssueType = Field(description="Type of error")
    codebase_folder: Optional[str] = Field(
        default=None, description="Codebase folder path"
    )
    codebase_workflow_run_id: Optional[str] = Field(
        default=None, description="The run ID of the codebase workflow"
    )
    error_message_body: str = Field(description="Error message")
    operation_type: RepositoryWorkflowOperation = Field(
        description="Operation type for generating contextual issue titles"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L329-L334` — `class IngestedRepositoryResponse(BaseModel):
    """Response model for ingested repository data."""

    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    provider_key: ProviderKey = Field(description="Provider key for this repository")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L337-L342` — `class IngestedRepositoriesListResponse(BaseModel):
    """Response model containing a list of ingested repositories."""

    repositories: List[IngestedRepositoryResponse] = Field(
        description="List of ingested repositories"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L345-L351` — `class RefreshRepositoryResponse(BaseModel):
    """Response after triggering repository refresh."""

    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    workflow_id: str = Field(description="The ID of the started workflow")
    run_id: str = Field(description="The run ID of the started workflow")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L354-L362` — `class CodebaseMetadataResponse(BaseModel):
    """Response model for individual codebase metadata."""

    codebase_folder: str = Field(
        description="Path to codebase folder relative to repo root"
    )
    programming_language_metadata: ProgrammingLanguageMetadata = Field(
        description="Language-specific metadata for this codebase"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L365-L372` — `class CodebaseMetadataListResponse(BaseModel):
    """Response model containing list of codebase metadata for a repository."""

    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    codebases: List[CodebaseMetadataResponse] = Field(
        description="List of codebase configurations with metadata"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L375-L380` — `class RepositoryProvidersResponse(BaseModel):
    """Response model containing list of configured repository providers."""

    providers: List[ProviderKey] = Field(
        description="List of configured repository provider keys"
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/parent_child_clone_metadata.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/parent_child_clone_metadata.py#L4-L6` — `class ParentChildCloneMetadata(BaseModel):
    repository_qualified_name: str
    codebase_qualified_names: list[str] = Field(default_factory=list)`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L36-L44` — `class RepoWorkflowRunEnvelope(BaseModel):
    repo_request: RepositoryRequestConfiguration
    github_token: str
    trace_id: str
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L47-L55` — `class GitActivityEnvelope(BaseModel):
    repo_request: RepositoryRequestConfiguration
    github_token: str
    trace_id: str
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L58-L65` — `class ConfluenceGitGraphEnvelope(BaseModel):
    git_repo: UnoplatGitRepository
    trace_id: str
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L68-L81` — `class CodebaseChildWorkflowEnvelope(BaseModel):
    repository_qualified_name: str
    codebase_qualified_name: str
    root_packages: List[str]
    codebase_path: str
    codebase_folder: str
    package_manager_metadata: UnoplatPackageManagerMetadata
    trace_id: str
    parent_workflow_run_id: Optional[str] = None
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L84-L92` — `class PackageMetadataActivityEnvelope(BaseModel):
    codebase_path: str
    programming_language_metadata: ProgrammingLanguageMetadata
    trace_id: str
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L95-L103` — `class PackageManagerMetadataIngestionEnvelope(BaseModel):
    codebase_qualified_name: str
    package_manager_metadata: UnoplatPackageManagerMetadata
    trace_id: str
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L106-L118` — `class CodebaseProcessingActivityEnvelope(BaseModel):
    root_packages: List[str]
    codebase_path: str
    repository_qualified_name: str
    codebase_qualified_name: str
    dependencies: Optional[List[str]]
    programming_language_metadata: ProgrammingLanguageMetadata
    trace_id: str
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/language_processors/language_processor_context.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/language_processors/language_processor_context.py#L18-L30` — `class LanguageProcessorContext(BaseModel):
    """Runtime context shared with language-specific processors."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    codebase_name: str
    codebase_path: Path
    root_packages: List[str]
    programming_language_metadata: ProgrammingLanguageMetadata
    env_config: EnvironmentSettings
    framework_detection_service: Optional[FrameworkDetectionService] = None
    concurrency_limit: int
    increment_files_processed: Callable[[int], None]`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/typescript/manifests/package_json_loader.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/typescript/manifests/package_json_loader.py#L28-L135` — `class PackageJsonManifest(BaseModel):
    """Normalized snapshot of package.json content for downstream TypeScript strategies."""

    model_config = ConfigDict(populate_by_name=True)

    manifest_path: Optional[str] = Field(
        default=None, description="Manifest path relative to the workspace root."
    )

    name: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    keywords: List[str] = Field(default_factory=list)
    author: Optional[Any] = Field(default=None)
    contributors: List[Any] = Field(default_factory=list)
    maintainers: List[Any] = Field(default_factory=list)
    license: Optional[Any] = Field(default=None)
    repository: Optional[Any] = Field(default=None)
    bugs: Optional[Any] = Field(default=None)
    homepage: Optional[str] = Field(default=None)
    documentation: Optional[str] = Field(default=None)
    readme: Optional[Any] = Field(default=None)

    dependencies: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Dependency groups extracted from package.json (default/dev/peer/optional/bundled/override).",
    )
    scripts: Dict[str, str] = Field(default_factory=dict)
    bin: Dict[str, str] = Field(default_factory=dict)
    exports: Optional[Any] = Field(default=None)
    types: Optional[str] = Field(default=None)
    main: Optional[str] = Field(default=None)
    module: Optional[str] = Field(default=None)
    types_versions: Optional[Dict[str, Any]] = Field(
        default=None, alias="typesVersions"
    )
    engines: Optional[Dict[str, Any]] = Field(default=None)

    package_manager_field: Optional[str] = Field(default=None, alias="packageManager")
    workspaces: Optional[Any] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def _build_from_raw(cls, data: Any, info: ValidationInfo) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("package.json content must deserialize to an object")

        context = info.context or {}
        manifest_path = context.get("manifest_path")
        manifest_directory = context.get("manifest_directory")
        if manifest_directory is not None and not isinstance(manifest_directory, Path):
            manifest_directory = Path(manifest_directory)

        # Only set fields that require special handling
        # Pydantic will automatically map all other fields from data by name
        transformed: Dict[str, Any] = {
            "manifest_path": manifest_path,
            "dependencies": _build_dependency_sections(data),
            "scripts": _ensure_dict(data.get("scripts"), section_name="scripts"),
            "engines": _ensure_dict(data.get("engines"), section_name="engines"),
        }

        # Merge original data with transformed fields
        # Transformed fields take precedence over original data
        return {**data, **transformed}

    @field_validator("bin", mode="before")
    @classmethod
    def _normalize_bin(cls, value: Any, info: ValidationInfo) -> Dict[str, str]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return {str(k): str(v) for k, v in value.items() if v is not None}
        if isinstance(value, str):
            package_name = getattr(info.data, "name", None)
            key = (
                package_name
                if isinstance(package_name, str) and package_name
                else "default"
            )
            return {key: value}
        logger.warning(
            "Unexpected bin section type", {"bin_type": type(value).__name__}
        )
        return {}

    @field_validator("keywords", mode="before")
    @classmethod
    def _normalize_keywords(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            return [value]
        logger.warning(
            "Unexpected keywords type", {"keywords_type": type(value).__name__}
        )
        return []

    @field_validator("contributors", "maintainers", mode="before")
    @classmethod
    def _ensure_list(cls, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/tree_sitter_config.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/tree_sitter_config.py#L13-L102` — `class TreeSitterExtractorConfig(BaseModel):
    """Configuration for Tree-sitter structural signature extraction.

    This model encapsulates all language-specific configuration needed
    by Tree-sitter extractors, providing a consistent pattern for Python,
    TypeScript, and future language implementations.

    Attributes:
        query_file_paths: Mapping of query type to `.scm` file path.
            Example keys: "module_functions", "class_methods", "global_variables"
        capture_mappings: Mapping of semantic keys to Tree-sitter capture names.
            Allows language-specific capture name customization while maintaining
            consistent semantic keys in the extractor code.
            Example: {"function": "docstring", "class": "class_docstring"}
        container_node_types: Set of AST node types that delimit top-level scope.
            Nodes with these types in their ancestry are NOT considered top-level.
            Example (Python): {"function_definition", "class_definition"}
        block_node_types: Set of AST node types representing code blocks.
            Used for navigation when determining immediate child relationships.
            Example (Python): {"block"}
        optional_query_keys: Set of query keys that can be missing without error.
            Enables gradual feature rollout and backward compatibility.
            Example: {"function_calls", "instance_variables", "nested_classes"}
        doc_cleaner: Optional callable to clean documentation string literals.
            Takes raw doc string and returns cleaned version.
            If None, returns doc strings unchanged.
            Example (Python): Strip triple quotes from docstrings

    Example:
        >>> from pathlib import Path
        >>> config = TreeSitterExtractorConfig(
        ...     query_file_paths={
        ...         "module_functions": Path("queries/python/module_functions.scm"),
        ...         "class_methods": Path("queries/python/class_methods.scm"),
        ...     },
        ...     capture_mappings={
        ...         "function": "docstring",
        ...         "class": "class_docstring",
        ...     },
        ...     container_node_types={"function_definition", "class_definition"},
        ...     block_node_types={"block"},
        ...     optional_query_keys={"function_calls"},
        ... )
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    query_file_paths: Dict[str, Path]
    capture_mappings: Dict[str, str] = Field(default_factory=dict)
    container_node_types: Set[str] = Field(default_factory=set)
    block_node_types: Set[str] = Field(default_factory=set)
    optional_query_keys: Set[str] = Field(default_factory=set)
    doc_cleaner: Callable[[str], str] = Field(default=lambda s: s)

    def get_capture_name(self, semantic_key: str) -> str:
        """Get Tree-sitter capture name for a semantic key.

        Falls back to the semantic key itself if no mapping exists,
        allowing flexibility in query file design.

        Args:
            semantic_key: Semantic identifier (e.g., "function", "class")

        Returns:
            Capture name to use in Tree-sitter queries (e.g., "docstring")

        Example:
            >>> config.get_capture_name("function")
            "docstring"
            >>> config.get_capture_name("unmapped_key")
            "unmapped_key"
        """
        return self.capture_mappings.get(semantic_key, semantic_key)

    def is_optional_query(self, query_key: str) -> bool:
        """Check if a query is optional and can be missing.

        Args:
            query_key: Query identifier (e.g., "function_calls")

        Returns:
            True if query can be missing without error, False otherwise

        Example:
            >>> config.is_optional_query("function_calls")
            True
            >>> config.is_optional_query("module_functions")
            False
        """
        return query_key in self.optional_query_keys`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/github_issues/models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/github_issues/models.py#L19-L24` — `class AgentRating(BaseModel):
    codebase_name: str = Field(description="Name of the codebase")
    agent_id: str = Field(description="Identifier of the agent")
    rating: Optional[SentimentRating] = Field(
        default=None, description="Optional sentiment rating for this agent"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/github_issues/models.py#L27-L42` — `class AgentFeedbackSubmissionRequest(BaseModel):
    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    parent_workflow_run_id: str = Field(description="The run ID of the parent workflow")
    overall_rating: SentimentRating = Field(
        description="Overall sentiment rating for the agent generation"
    )
    agent_ratings: Optional[List[AgentRating]] = Field(
        default=None, description="Optional per-agent ratings for detailed feedback"
    )
    categories: List[FeedbackCategory] = Field(
        default_factory=list, description="Categories of feedback"
    )
    comments: Optional[str] = Field(
        default=None, description="Optional free-form comments"
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/github_app/models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/github_app/models.py#L18-L38` — `class GithubAppManifestRecord(SQLBase):
    """Database record tracking active manifest states awaiting conversion."""

    __tablename__ = "github_app_manifest_request"
    __table_args__ = (
        Index(
            "ix_github_app_manifest_request_expires_at",
            "expires_at",
        ),
    )

    state: Mapped[str] = mapped_column(primary_key=True)
    manifest_json: Mapped[str] = mapped_column(Text, nullable=False)
    owner_login: Mapped[Optional[str]] = mapped_column(nullable=True)
    owner_type: Mapped[str] = mapped_column(nullable=False, default="user")
    registration_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    requested_by: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/github_app/models.py#L41-L81` — `class ManifestGenerationRequest(BaseModel):
    """Incoming payload for initiating the manifest flow."""

    owner: Optional[str] = Field(
        default=None,
        description=(
            "GitHub username or organization slug that will own the GitHub App. "
            "Falls back to service defaults when omitted."
        ),
    )
    owner_type: Literal["user", "organization"] = Field(
        default="user",
        description="Determines whether to use /settings/apps/new or /organizations/{owner}/settings/apps/new.",
    )
    service_base_url: AnyHttpUrl = Field(
        description="Base URL where this service is reachable (e.g. https://bridge.example.com).",
    )
    webhook_proxy_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Optional webhook proxy (e.g. smee.io) used in place of the service webhook for local testing.",
    )
    app_name: Optional[str] = Field(
        default=None,
        description="Optional override for the GitHub App name; defaults to the service configuration.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional override for the GitHub App description.",
    )
    homepage_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Optional override for the GitHub App homepage URL.",
    )
    post_install_redirect_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Optional URL GitHub should redirect to after the installation completes.",
    )
    requested_by: Optional[str] = Field(
        default=None,
        description="Opaque identifier representing the operator that initiated the manifest flow.",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/github_app/models.py#L84-L105` — `class ManifestGenerationResponse(BaseModel):
    """Response payload returned to the operator initiating the manifest flow."""

    state: str = Field(
        description="Opaque state token that must be echoed back by GitHub."
    )
    manifest: Dict[str, Any] = Field(
        description="Final manifest JSON submitted to GitHub."
    )
    registration_url: AnyHttpUrl = Field(
        description="GitHub URL the operator should open to register the manifest."
    )
    owner: Optional[str] = Field(
        default=None, description="Effective owner slug resolved for the manifest."
    )
    owner_type: Literal["user", "organization"] = Field(
        description="Owner type that will receive the GitHub App."
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp (UTC) when the manifest state will expire if unused.",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/github_app/models.py#L108-L122` — `class ManifestConversionResponse(BaseModel):
    """Response payload returned after exchanging the manifest code with GitHub."""

    app_slug: str = Field(description="Short slug assigned to the created GitHub App.")
    app_id: int = Field(description="Numeric identifier of the created GitHub App.")
    client_id: str = Field(
        description="OAuth client identifier associated with the app."
    )
    html_url: AnyHttpUrl = Field(description="GitHub UI URL for managing the app.")
    installation_url: AnyHttpUrl = Field(
        description="URL the operator should visit to install the GitHub App."
    )
    instructions: List[str] = Field(
        description="Ordered list of recommended follow-up steps for the operator."
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L15-L25` — `class GitHubOwner(BaseModel):
    """GitHub repository owner model."""

    login: str = Field(description="The username of the owner")
    id: int = Field(description="Unique identifier of the owner")
    node_id: str = Field(description="Node ID of the owner")
    avatar_url: str = Field(description="URL to the owner's avatar")
    html_url: str = Field(description="HTML URL of the owner")
    type: str = Field(description="Type of the owner (User, Organization)")
    site_admin: bool = Field(description="Whether the owner is a site admin")
    url: str = Field(description="API URL of the owner")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L28-L35` — `class GitHubLicense(BaseModel):
    """GitHub repository license model."""

    key: str = Field(description="License key")
    name: str = Field(description="License name")
    url: Optional[str] = Field(default=None, description="License URL")
    spdx_id: Optional[str] = Field(default=None, description="SPDX ID of the license")
    node_id: str = Field(description="Node ID of the license")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L38-L84` — `class GitHubRepo(BaseModel):
    """Model for GitHub repository data based on GitHub API response."""

    id: int = Field(description="Unique identifier of the repository")
    node_id: str = Field(description="Node ID of the repository")
    name: str = Field(description="The name of the repository")
    full_name: str = Field(description="Full name of the repository (owner/repo)")
    private: bool = Field(description="Whether the repository is private")
    owner: GitHubOwner = Field(description="Owner of the repository")
    html_url: str = Field(description="HTML URL of the repository")
    description: Optional[str] = Field(
        default=None, description="Repository description"
    )
    fork: bool = Field(description="Whether the repository is a fork")
    url: str = Field(description="API URL of the repository")
    git_url: str = Field(description="Git URL of the repository")
    ssh_url: str = Field(description="SSH URL of the repository")
    clone_url: str = Field(description="Clone URL of the repository")
    default_branch: str = Field(description="Default branch of the repository")
    created_at: Optional[str] = Field(
        default=None, description="Repository creation date"
    )
    updated_at: Optional[str] = Field(
        default=None, description="Repository last update date"
    )
    pushed_at: Optional[str] = Field(default=None, description="Last push date")
    language: Optional[str] = Field(
        default=None, description="Primary language of the repository"
    )
    license: Optional[GitHubLicense] = Field(
        default=None, description="Repository license"
    )
    forks_count: int = Field(description="Number of forks")
    stargazers_count: int = Field(description="Number of stars")
    watchers_count: int = Field(description="Number of watchers")
    size: int = Field(description="Size of the repository in KB")
    open_issues_count: int = Field(description="Number of open issues")
    topics: Optional[List[str]] = Field(default=None, description="Repository topics")
    has_issues: bool = Field(description="Whether issues are enabled")
    has_projects: bool = Field(description="Whether projects are enabled")
    has_wiki: bool = Field(description="Whether the wiki is enabled")
    has_pages: bool = Field(description="Whether GitHub Pages is enabled")
    archived: bool = Field(description="Whether the repository is archived")
    disabled: bool = Field(description="Whether the repository is disabled")
    visibility: Optional[str] = Field(
        default=None, description="Repository visibility (public, private, internal)"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L87-L94` — `class GitHubRepoSummary(BaseModel):
    """Simplified model for GitHub repository data."""

    name: str = Field(description="The name of the repository")
    owner_url: str = Field(description="HTML URL of the repository owner")
    private: bool = Field(description="Whether the repository is private")
    git_url: str = Field(description="Git URL of the repository")
    owner_name: str = Field(description="Login of the repository owner")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L97-L103` — `class PaginatedResponse(BaseModel):
    items: List[GitHubRepoSummary]
    per_page: int = Field(description="Number of items per page")
    has_next: bool = Field(description="Whether there are more items to fetch")
    next_cursor: Optional[str] = Field(
        default=None, description="Cursor for the next page of results"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L111-L126` — `class IssueTracking(BaseModel):
    issue_id: Optional[str] = Field(
        default=None, description="Issue ID associated with the error"
    )
    issue_number: Optional[int] = Field(
        default=None, description="Issue number in the GitHub repository"
    )
    issue_url: Optional[str] = Field(
        default=None, description="Issue URL associated with the error"
    )
    issue_status: Optional[IssueStatus] = Field(
        default=None, description="Issue status associated with the error"
    )
    created_at: Optional[str] = Field(
        default=None, description="Timestamp when the issue was created"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L129-L145` — `class WorkflowRun(BaseModel):
    codebase_workflow_run_id: str = Field(
        description="Unique identifier for this specific run instance of the workflow."
    )
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    status: JobStatus = Field(
        description="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED."
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the workflow run completed"
    )
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error report if the workflow run failed"
    )
    issue_tracking: Optional[IssueTracking] = Field(
        default=None, description="GitHub issue tracking info for the workflow run"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L148-L154` — `class WorkflowStatus(BaseModel):
    codebase_workflow_id: str = Field(
        description="Unique identifier for the workflow (remains constant across execution runs)."
    )
    codebase_workflow_runs: List[WorkflowRun] = Field(
        description="Multiple run instances for this workflow."
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L157-L161` — `class CodebaseStatus(BaseModel):
    codebase_folder: str = Field(description="The folder path of the codebase.")
    workflows: List[WorkflowStatus] = Field(
        description="List of workflows under this codebase."
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L164-L167` — `class CodebaseStatusList(BaseModel):
    codebases: List[CodebaseStatus] = Field(
        description="List of codebases each with multiple workflows."
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L170-L182` — `class RepositoryRequestConfiguration(BaseModel):
    """Configuration for a repository ingestion request, including codebase config and provider credentials."""

    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_git_url: str = Field(description="The git URL of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_metadata: Optional[List[CodebaseConfig]] = Field(
        default=None,
        description="List of codebase configurations for the repository (auto-detected if not provided)",
    )
    provider_key: ProviderKey = Field(
        ..., description="Provider key for credential and repository provider lookup"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L185-L196` — `class RepositoryRefreshRequest(BaseModel):
    """Minimal payload accepted by the refresh endpoint."""

    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_owner_name: str = Field(description="The name of the repository owner")
    provider_key: ProviderKey = Field(
        ..., description="Provider key for credential lookup during refresh"
    )
    repository_git_url: Optional[str] = Field(
        default=None,
        description="Optional git URL override. If omitted, the backend derives it from provider metadata.",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L199-L206` — `class GitHubRepoResponseConfiguration(BaseModel):
    """Configuration for a GitHub repository, including codebase config and status."""

    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_metadata: List[CodebaseConfig] = Field(
        description="List of codebase configurations for the repository"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L209-L227` — `class CodebaseCurrentStatus(BaseModel):
    """Model for current status of a single codebase workflow run."""

    codebase_folder: str = Field(description="The folder path of the codebase")
    codebase_workflow_run_id: str = Field(
        description="The run ID of the codebase workflow"
    )
    codebase_workflow_id: str = Field(description="The ID of the codebase workflow")
    status: JobStatus = Field(description="Status of the workflow run")
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    completed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the workflow run completed"
    )
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error report if the workflow run failed"
    )
    issue_tracking: Optional[IssueTracking] = Field(
        default=None, description="GitHub issue tracking info for the workflow run"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L230-L256` — `class GithubRepoStatus(BaseModel):
    """Model for current status of a repository workflow run and its associated codebase runs."""

    repository_name: str = Field(description="The name of the repository (primary key)")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_workflow_run_id: str = Field(
        description="The run ID of the repository workflow"
    )
    repository_workflow_id: str = Field(description="The ID of the repository workflow")
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    status: JobStatus = Field(
        description="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED."
    )
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error report if the workflow run failed"
    )
    issue_tracking: Optional[IssueTracking] = Field(
        default=None,
        description="GitHub issue tracking info for the repository workflow run",
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the workflow run completed"
    )
    codebase_status_list: Optional[CodebaseStatusList] = Field(
        default=None,
        description="Status of the repository workflows (optional, returned in GET)",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L259-L280` — `class ParentWorkflowJobResponse(BaseModel):
    """Response model for parent workflow job data API."""

    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    repository_workflow_run_id: str = Field(
        description="The run ID of the repository workflow"
    )
    operation: RepositoryWorkflowOperation = Field(
        description="Operation type of the workflow run. One of: INGESTION, AGENTS_GENERATION, AGENT_MD_UPDATE."
    )
    status: JobStatus = Field(
        description="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING."
    )
    started_at: datetime = Field(description="Timestamp when the workflow run started")
    completed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the workflow run completed"
    )
    feedback_issue_url: Optional[str] = Field(
        default=None,
        description="URL of the GitHub issue created from agent feedback submission",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L283-L288` — `class ParentWorkflowJobListResponse(BaseModel):
    """Response model containing a list of parent workflow job data."""

    jobs: List[ParentWorkflowJobResponse] = Field(
        description="List of parent workflow jobs"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L296-L310` — `class GithubIssueSubmissionRequest(BaseModel):
    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    parent_workflow_run_id: str = Field(description="The run ID of the parent workflow")
    error_type: IssueType = Field(description="Type of error")
    codebase_folder: Optional[str] = Field(
        default=None, description="Codebase folder path"
    )
    codebase_workflow_run_id: Optional[str] = Field(
        default=None, description="The run ID of the codebase workflow"
    )
    error_message_body: str = Field(description="Error message")
    operation_type: RepositoryWorkflowOperation = Field(
        description="Operation type for generating contextual issue titles"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L313-L318` — `class IngestedRepositoryResponse(BaseModel):
    """Response model for ingested repository data."""

    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    provider_key: ProviderKey = Field(description="Provider key for this repository")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L321-L326` — `class IngestedRepositoriesListResponse(BaseModel):
    """Response model containing a list of ingested repositories."""

    repositories: List[IngestedRepositoryResponse] = Field(
        description="List of ingested repositories"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L329-L335` — `class RefreshRepositoryResponse(BaseModel):
    """Response after triggering repository refresh."""

    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    workflow_id: str = Field(description="The ID of the started workflow")
    run_id: str = Field(description="The run ID of the started workflow")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L338-L346` — `class CodebaseMetadataResponse(BaseModel):
    """Response model for individual codebase metadata."""

    codebase_folder: str = Field(
        description="Path to codebase folder relative to repo root"
    )
    programming_language_metadata: ProgrammingLanguageMetadata = Field(
        description="Language-specific metadata for this codebase"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L349-L356` — `class CodebaseMetadataListResponse(BaseModel):
    """Response model containing list of codebase metadata for a repository."""

    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    codebases: List[CodebaseMetadataResponse] = Field(
        description="List of codebase configurations with metadata"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py#L359-L364` — `class RepositoryProvidersResponse(BaseModel):
    """Response model containing list of configured repository providers."""

    providers: List[ProviderKey] = Field(
        description="List of configured repository provider keys"
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L16-L39` — `class UnoplatCodeConfluenceGitRepository(SQLBase):
    """Git repository stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_git_repository"
    __table_args__ = (
        Index("uq_cc_git_repo_url", "repository_url", unique=True),
        {"extend_existing": True},
    )

    qualified_name: Mapped[str] = mapped_column(primary_key=True)
    repository_url: Mapped[str] = mapped_column(nullable=False)
    repository_name: Mapped[str] = mapped_column(nullable=False)
    repository_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None
    )
    readme: Mapped[Optional[str]] = mapped_column(default=None)
    domain: Mapped[Optional[str]] = mapped_column(default=None)
    github_organization: Mapped[Optional[str]] = mapped_column(default=None)

    codebases: Mapped[List["UnoplatCodeConfluenceCodebase"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L42-L84` — `class UnoplatCodeConfluenceCodebase(SQLBase):
    """Codebase stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_codebase"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_qualified_name"],
            ["code_confluence_git_repository.qualified_name"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    qualified_name: Mapped[str] = mapped_column(primary_key=True)
    repository_qualified_name: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    readme: Mapped[Optional[str]] = mapped_column(default=None)
    root_packages: Mapped[Optional[List[str]]] = mapped_column(JSONB, default=None)
    codebase_path: Mapped[str] = mapped_column(nullable=False)
    codebase_folder: Mapped[Optional[str]] = mapped_column(default=None)
    programming_language: Mapped[Optional[str]] = mapped_column(default=None)

    repository: Mapped[UnoplatCodeConfluenceGitRepository] = relationship(
        back_populates="codebases"
    )
    package_manager_metadata: Mapped[
        Optional["UnoplatCodeConfluencePackageManagerMetadata"]
    ] = relationship(
        back_populates="codebase",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    files: Mapped[List["UnoplatCodeConfluenceFile"]] = relationship(
        back_populates="codebase",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    frameworks: Mapped[List["UnoplatCodeConfluenceCodebaseFramework"]] = relationship(
        back_populates="codebase",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L87-L114` — `class UnoplatCodeConfluencePackageManagerMetadata(SQLBase):
    """Package manager metadata stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_package_manager_metadata"
    __table_args__ = (
        ForeignKeyConstraint(
            ["codebase_qualified_name"],
            ["code_confluence_codebase.qualified_name"],
            ondelete="CASCADE",
        ),
        Index(
            "uq_cc_pkg_metadata_codebase",
            "codebase_qualified_name",
            unique=True,
        ),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codebase_qualified_name: Mapped[str] = mapped_column(nullable=False)
    dependencies: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    other_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    package_manager: Mapped[str] = mapped_column(nullable=False)
    programming_language: Mapped[str] = mapped_column(nullable=False)

    codebase: Mapped[UnoplatCodeConfluenceCodebase] = relationship(
        back_populates="package_manager_metadata"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L117-L149` — `class UnoplatCodeConfluenceFile(SQLBase):
    """Source file stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_file"
    __table_args__ = (
        ForeignKeyConstraint(
            ["codebase_qualified_name"],
            ["code_confluence_codebase.qualified_name"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    file_path: Mapped[str] = mapped_column(primary_key=True)
    codebase_qualified_name: Mapped[str] = mapped_column(nullable=False)
    checksum: Mapped[Optional[str]] = mapped_column(default=None)
    structural_signature: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None
    )
    imports: Mapped[List[str]] = mapped_column(JSONB, default=list)
    has_data_model: Mapped[bool] = mapped_column(default=False)
    data_model_positions: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    codebase: Mapped[UnoplatCodeConfluenceCodebase] = relationship(
        back_populates="files"
    )
    framework_features: Mapped[List["UnoplatCodeConfluenceFileFrameworkFeature"]] = (
        relationship(
            back_populates="file",
            cascade="all, delete-orphan",
            passive_deletes=True,
        )
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L152-L176` — `class UnoplatCodeConfluenceCodebaseFramework(SQLBase):
    """Join table linking codebases to frameworks."""

    __tablename__ = "code_confluence_codebase_framework"
    __table_args__ = (
        ForeignKeyConstraint(
            ["codebase_qualified_name"],
            ["code_confluence_codebase.qualified_name"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["framework_language", "framework_library"],
            ["framework.language", "framework.library"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    codebase_qualified_name: Mapped[str] = mapped_column(primary_key=True)
    framework_language: Mapped[str] = mapped_column(primary_key=True)
    framework_library: Mapped[str] = mapped_column(primary_key=True)

    codebase: Mapped[UnoplatCodeConfluenceCodebase] = relationship(
        back_populates="frameworks"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L179-L211` — `class UnoplatCodeConfluenceFileFrameworkFeature(SQLBase):
    """Join table linking files to framework features with span metadata."""

    __tablename__ = "code_confluence_file_framework_feature"
    __table_args__ = (
        ForeignKeyConstraint(
            ["file_path"],
            ["code_confluence_file.file_path"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["feature_language", "feature_library", "feature_key"],
            [
                "framework_feature.language",
                "framework_feature.library",
                "framework_feature.feature_key",
            ],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    file_path: Mapped[str] = mapped_column(primary_key=True)
    feature_language: Mapped[str] = mapped_column(primary_key=True)
    feature_library: Mapped[str] = mapped_column(primary_key=True)
    feature_key: Mapped[str] = mapped_column(primary_key=True)
    start_line: Mapped[int] = mapped_column(primary_key=True)
    end_line: Mapped[int] = mapped_column(primary_key=True)
    match_text: Mapped[Optional[str]] = mapped_column(Text, default=None)

    file: Mapped[UnoplatCodeConfluenceFile] = relationship(
        back_populates="framework_features"
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/repo_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/repo_models.py#L39-L73` — `class Repository(SQLBase):
    """SQLModel for repository table in code_confluence schema."""

    __tablename__ = "repository"

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    repository_provider: Mapped[ProviderKey] = mapped_column(
        SQLEnum(ProviderKey, name="repository_provider_type", native_enum=False),
        default=ProviderKey.GITHUB_OPEN,
        nullable=False,
        comment="Provider key for this repository (e.g., GITHUB_OPEN, GITHUB_ENTERPRISE, GITLAB_CE, GITLAB_ENTERPRISE)",
    )

    # Relationships - will be populated after class definitions
    workflow_runs: Mapped[List["RepositoryWorkflowRun"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    configs: Mapped[List["CodebaseConfig"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    agent_md_snapshot: Mapped[Optional["RepositoryAgentMdSnapshot"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/repo_models.py#L76-L112` — `class CodebaseConfig(SQLBase):
    """SQLModel for codebase_config table in code_confluence schema."""

    __tablename__ = "codebase_config"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    codebase_folder: Mapped[str] = mapped_column(
        primary_key=True, comment="Path to codebase folder relative to repo root"
    )
    root_packages: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, default=None, comment="List of root packages within the codebase folder"
    )
    programming_language_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Language-specific metadata for this codebase like programming language, package manager etc",
    )

    # Relationships
    repository: Mapped[Repository] = relationship(back_populates="configs")
    workflow_runs: Mapped[List["CodebaseWorkflowRun"]] = relationship(
        back_populates="codebase_config",
        viewonly=True,
        overlaps="repository_workflow_run,workflow_runs",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/repo_models.py#L115-L191` — `class RepositoryWorkflowRun(SQLBase):
    """SQLModel for repository_workflow_run table in code_confluence schema."""

    __tablename__ = "repository_workflow_run"
    __table_args__ = (
        CheckConstraint(
            "status IN ('SUBMITTED','RUNNING','FAILED','TIMED_OUT','COMPLETED','RETRYING','ERROR','CANCELLED')",
            name="status_check",
        ),
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True, comment="The run ID of the repository workflow"
    )
    repository_workflow_id: Mapped[str] = mapped_column(
        comment="The ID of the repository workflow"
    )
    operation: Mapped[RepositoryWorkflowOperation] = mapped_column(
        SQLEnum(
            RepositoryWorkflowOperation,
            name="repository_workflow_operation_type",
            native_enum=False,
        ),
        default=RepositoryWorkflowOperation.INGESTION,
        nullable=False,
        comment="Operation this workflow run performs (e.g., INGESTION, AGENTS_GENERATION, AGENT_MD_UPDATE)",
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING, ERROR, CANCELLED.",
    )
    error_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None, comment="Error report if the workflow run failed"
    )
    issue_tracking: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=None,
        comment="GitHub issue tracking info for this repository workflow run",
    )
    feedback_issue_url: Mapped[Optional[str]] = mapped_column(
        String,
        default=None,
        nullable=True,
        comment="GitHub issue URL for user feedback on agent generation",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when the workflow run started",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp when the workflow run completed",
    )

    # Relationships
    repository: Mapped[Repository] = relationship(back_populates="workflow_runs")
    codebase_workflow_runs: Mapped[List["CodebaseWorkflowRun"]] = relationship(
        back_populates="repository_workflow_run",
        viewonly=True,
        overlaps="codebase_config,workflow_runs",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/repo_models.py#L194-L274` — `class CodebaseWorkflowRun(SQLBase):
    """SQLModel for codebase_workflow_run table in code_confluence schema."""

    __tablename__ = "codebase_workflow_run"
    __table_args__ = (
        CheckConstraint(
            "status IN ('SUBMITTED','RUNNING','FAILED','TIMED_OUT','COMPLETED','RETRYING','ERROR','CANCELLED')",
            name="codebase_status_check",
        ),
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name", "codebase_folder"],
            [
                "codebase_config.repository_name",
                "codebase_config.repository_owner_name",
                "codebase_config.codebase_folder",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name", "repository_workflow_run_id"],
            [
                "repository_workflow_run.repository_name",
                "repository_workflow_run.repository_owner_name",
                "repository_workflow_run.repository_workflow_run_id",
            ],
            ondelete="CASCADE",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    codebase_folder: Mapped[str] = mapped_column(
        primary_key=True, comment="FK to codebase_config - path to codebase folder"
    )
    codebase_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Unique identifier for this specific run of the codebase workflow",
    )
    codebase_workflow_id: Mapped[str] = mapped_column(
        comment="The ID of the codebase workflow"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        comment="Link back to parent repository workflow run"
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING, ERROR, CANCELLED.",
    )
    error_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None, comment="Error report if the workflow run failed"
    )
    issue_tracking: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=None,
        comment="GitHub issue tracking info for this codebase workflow run",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when the workflow run started",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp when the workflow run completed",
    )

    # Relationships
    codebase_config: Mapped[CodebaseConfig] = relationship(
        back_populates="workflow_runs"
    )
    repository_workflow_run: Mapped[RepositoryWorkflowRun] = relationship(
        back_populates="codebase_workflow_runs"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/framework_samples/unoplat_code_confluence_commons/repo_models.py#L277-L378` — `class RepositoryAgentMdSnapshot(SQLBase):
    """SQLModel for repository_agent_md_snapshot table in code_confluence schema."""

    __tablename__ = "repository_agent_md_snapshot"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            [
                "repository_name",
                "repository_owner_name",
                "repository_workflow_run_id",
            ],
            [
                "repository_workflow_run.repository_name",
                "repository_workflow_run.repository_owner_name",
                "repository_workflow_run.repository_workflow_run_id",
            ],
            ondelete="CASCADE",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True,
        comment="The run ID of the repository workflow this snapshot belongs to",
    )
    events: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Events and progress captured during agent execution",
    )

    event_counters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment=(
            "Per-codebase event ID seeds to ensure monotonic append across workers,"
            ' e.g., {"codebase": {"next_id": 7}}.sequence number for this codebase’s event stream'
        ),
    )

    codebase_progress: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment=(
            "Per-codebase progress state persisted in the DB:"
            ' {"codebase": {"progress": 66.67,'
            ' "completed_namespaces": ["project_configuration_agent"]}}'
        ),
    )

    agent_md_output: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Complete final payload from agent execution containing per-codebase agent data",
    )
    statistics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="Aggregated usage and pricing statistics for the latest agent workflow",
    )
    overall_progress: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        default=None,
        comment="Cached overall progress percentage for fast polling",
    )
    latest_event_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp of the most recent appended event for this run",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Timestamp when the row was first inserted",
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the latest overwrite occurred",
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(back_populates="agent_md_snapshot")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py#L28-L31` — `class ProgrammingLanguageMetadata(BaseModel):
    language: ProgrammingLanguage
    package_manager: PackageManagerType
    language_version: Optional[str] = None`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py#L34-L37` — `class CodebaseConfig(BaseModel):
    codebase_folder: str
    root_package: Optional[str] = None
    programming_language_metadata: ProgrammingLanguageMetadata`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py#L40-L43` — `class RepositorySettings(BaseModel):
    git_url: str
    output_path: str
    codebases: List[CodebaseConfig]`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py#L46-L48` — `class ArchGuardConfig(BaseModel):
    download_url: str
    download_directory: str`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py#L51-L53` — `class LLMProviderConfig(BaseModel):
    llm_model_provider: str
    llm_model_provider_args: Dict[str, Any]`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py#L56-L58` — `class DatabaseConfig(BaseModel):
    name: DatabaseType
    uri: str`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py#L61-L63` — `class DatabaseSettings(BaseModel):
    host: str
    port: int`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py#L67-L82` — `class AppConfig(BaseModel):
    """JSON configuration"""

    repositories: List[RepositorySettings]
    llm_provider_config: Optional[LLMProviderConfig] = None
    databases: Optional[List[DatabaseConfig]] = None
    json_output: Optional[bool] = None
    sentence_transformer_model: Optional[str] = None

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "AppConfig":
        """Load configuration from JSON file"""
        config_file = config_path or "config.json"
        with open(config_file, "r") as f:
            config_data = json.loads(f.read())
        return cls(**config_data)`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/models/user_model.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/models/user_model.py#L8-L14` — `User`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/models/user_model.py#L18-L23` — `UserProfile`
