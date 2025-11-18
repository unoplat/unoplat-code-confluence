# Code Confluence Flow Bridge - Claude Code Integration Guide

## Project Overview

Code Confluence Flow Bridge is the backend ingestion service for the Unoplat Code Confluence system. It orchestrates repository processing workflows using Temporal, parses code structures using Tree-sitter, and stores results in Neo4j graph and PostgreSQL relational databases.

### Key Responsibilities
- **Workflow Orchestration**: Temporal-based workflows for repository and codebase processing
- **Code Parsing**: Language-agnostic parsing using Tree-sitter (Python and TypeScript support)
- **Graph Persistence**: Neo4j storage for code structure and relationships
- **Metadata Management**: PostgreSQL for workflow state, credentials, and configuration
- **Multi-language Support**: Framework detection and package manager analysis

## Essential Development Commands

### Dependency Management
```bash
# Sync dependencies (required before running)
task sync

# Update a specific package
task update-package PACKAGE=package_name

# Update all packages
task update-all-packages
```

### Development Workflow
```bash
# Start all dependencies (PostgreSQL, Neo4j, Temporal, Elasticsearch)
task start-dependencies

# Start only core dependencies (without Signoz/OpenTelemetry)
task start-core-dependencies

# Run FastAPI server in development mode
task run-dev        # Requires dependencies already running
task dev            # Starts dependencies then runs FastAPI

# Stop all dependencies
task stop-dependencies
task stop-core-dependencies
```

### Testing & Code Quality
```bash
# Run tests with coverage
task test

# Linting
task lint           # Check with ruff
task lint-fix       # Auto-fix issues

# Type checking
task typecheck      # Full type check
task typecheck-file FILE=path/to/file.py

# Code formatting
task format         # Format with ruff

# Framework definition validation
task validate-framework-definitions
task validate-single-framework FILE=framework-definitions/python/fastapi.json
```

### GitHub Integration
```bash
# Submit test job to flow bridge
task run-client    # Uses CLI config to test ingestion

# Run GitHub Actions locally
task run-github-action-locally
```

## Architecture Overview

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Application (main.py)                │
│  - Token management endpoints                                │
│  - Repository discovery (GitHub GraphQL)                    │
│  - Ingestion orchestration                                  │
│  - Status tracking and deletion                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   Temporal      PostgreSQL        Neo4j
   Workflows     (Metadata)      (Graph DB)
        │
   ┌────┴─────┬──────────┬──────────────┐
   │           │          │              │
   ▼           ▼          ▼              ▼
RepoWorkflow  Git      Package      Codebase
             Activity  Metadata    Processing
                      Activity     Activity
```

### Workflow Orchestration (Temporal)

**Parent Workflow**: `RepoWorkflow` (class-based)
- Orchestrates entire repository ingestion process
- Manages child workflows for each codebase
- Task Queue: `unoplat-code-confluence-repository-context-ingestion`

**Key Activities** (executed by worker pool):
1. **GitActivity** - Clones repository, extracts metadata
2. **ConfluenceGitGraph** - Inserts repository structure into Neo4j
3. **PackageMetadataActivity** - Extracts dependency information
4. **PackageManagerMetadataIngestion** - Stores package data in Neo4j
5. **GenericCodebaseProcessingActivity** - Parses code and creates graph nodes
6. **ChildWorkflowDbActivity** - Updates codebase workflow status in PostgreSQL
7. **ParentWorkflowDbActivity** - Updates repository workflow status in PostgreSQL

**Child Workflow**: `CodebaseChildWorkflow`
- Processes individual codebases detected in repository
- Handles language-specific parsing and metadata extraction

### Data Flow

1. **Repository Discovery**
   - Frontend requests repository list via GraphQL
   - Backend fetches from GitHub (GITHUB_OPEN or GITHUB_ENTERPRISE)
   - Credentials encrypted/stored in PostgreSQL

2. **Codebase Detection**
   - Auto-detection using multi-language ripgrep detectors
   - Supported: Python (PythonRipgrepDetector), TypeScript (TypeScriptRipgrepDetector)
   - Returns: List of CodebaseConfig with metadata

3. **Ingestion Workflow**
   - Temporal workflow clones repository to `/opt/unoplat/repositories`
   - GitActivity creates UnoplatGitRepository structure
   - ConfluenceGitGraph inserts repository node into Neo4j
   - Child workflows spawn for each detected codebase

4. **Code Parsing**
   - GenericCodebaseParser uses language processors
   - Tree-sitter extracts structural signatures
   - Framework detection (Python: FastAPI, Django, Flask, etc.)
   - Package manager parsing (pip, uv, poetry, npm, yarn, etc.)

5. **Persistence**
   - PostgreSQL: Workflow runs, credentials, framework definitions
   - Neo4j: Repository, File, Class, Function, Package nodes with relationships

### Database Configuration

**PostgreSQL** (via SQLAlchemy async + asyncpg)
- Connection URL: `postgresql+asyncpg://user:password@host:port/db`
- Session management: Per-loop async engine pattern (see `db.py`)
- Models: SQLBase from commons (Repository, CodebaseConfig, RepositoryWorkflowRun, CodebaseWorkflowRun)

**Neo4j** (via neomodel + neo4j driver)
- Connection URL: `bolt://user:password@host:port`
- Uses async driver for non-blocking operations
- Global connection via `CodeConfluenceGraph` singleton
- Schema: Installed at startup via `adb.install_all_labels()`

**Environment Variables** (from `EnvironmentSettings`):
```python
# PostgreSQL
DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# Neo4j
NEO4J_HOST, NEO4J_PORT, NEO4J_USERNAME, NEO4J_PASSWORD
NEO4J_MAX_CONNECTION_LIFETIME, NEO4J_MAX_CONNECTION_POOL_SIZE
NEO4J_CONNECTION_ACQUISITION_TIMEOUT

# Temporal
TEMPORAL_SERVER_ADDRESS (default: localhost:7233)
TEMPORAL_MAX_CONCURRENT_ACTIVITIES (default: 4)
TEMPORAL_ENABLE_POLLER_AUTOSCALING (default: false)

# Repositories
REPOSITORIES_BASE_PATH (default: ~/.unoplat/repositories)

# Framework definitions
FRAMEWORK_DEFINITIONS_PATH (default: /framework-definitions)
```

## Important Architecture Patterns

### 1. Envelope Pattern (Temporal Parameters)

All Temporal workflow/activity parameters are wrapped in envelope models to handle extra fields:

```python
# Example: RepoWorkflowRunEnvelope
@dataclass
class RepoWorkflowRunEnvelope(BaseModel):
    repo_request: RepositoryRequestConfiguration  # Main payload
    github_token: str
    trace_id: str
    model_config = ConfigDict(extra="allow")  # Allow extra fields
    
    @property
    def extras(self) -> dict[str, Any]:
        return dict(self.model_extra or {})
```

All envelope models support `extra="allow"` to handle Pydantic data converter requirements.

### 2. Async Database Session Management

Critical pattern for handling multiple event loops:

```python
# Gets or creates AsyncEngine per event loop
engine, session_factory = await get_engine_for_loop()

# Yields session for dependency injection
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        async with session.begin():  # Explicit transaction
            yield session
            # Commit on __exit__, rollback on exception

# For context managers (activities)
async with get_session_cm() as session:
    await session.execute(...)  # Auto-committed on context exit
```

**Key Points**:
- Each event loop gets its own AsyncEngine (fixes Temporal activity issues)
- `expire_on_commit=False` critical for async (prevents implicit I/O)
- Always use `async with session.begin()` for explicit transactions
- Activities in Temporal need context manager pattern for cleanup

### 3. Temporal Worker Configuration

Worker handles both parent and child workflows with interceptors:

```python
worker = Worker(
    client,
    task_queue="unoplat-code-confluence-repository-context-ingestion",
    workflows=[RepoWorkflow, CodebaseChildWorkflow],
    activities=activities,
    activity_executor=ThreadPoolExecutor(size=max_concurrent + 4),
    interceptors=[
        ParentWorkflowStatusInterceptor(),  # Updates parent workflow status
        ActivityStatusInterceptor(),        # Updates activity status
    ],
    max_concurrent_activities=env.temporal_max_concurrent_activities,
)
```

### 4. Parser Factory Pattern

Language-specific parsing via strategy pattern:

```python
# Generic parser delegates to language-specific processors
parser = GenericCodebaseParser(
    codebase_name="my-app",
    codebase_path="/repo/src",
    language_metadata=ProgrammingLanguageMetadata(...),
)

# Internally uses:
# - PythonLanguageProcessor (wraps TreeSitterPythonStructuralSignatureExtractor)
# - TypeScriptLanguageProcessor
# - Custom processors for other languages
```

### 5. Package Manager Strategy

Different strategies for different package managers:

```python
# Strategy pattern for package manager processing
class PackageManagerStrategy(ABC):
    @abstractmethod
    def process_metadata(
        self, 
        local_workspace_path: str, 
        metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        pass
```

Implementations available for: pip, uv, poetry, npm, yarn, maven, etc.

### 6. Neo4j Session Management

Uses neomodel's managed transactions pattern:

```python
# Get session from global connection
async with code_confluence_graph.get_session() as neo4j_session:
    # Use session.execute_write() or execute_read() for managed transactions
    result = await neo4j_session.execute_write(some_function, arg1, arg2)
```

Automatic retry and transaction management via Neo4j driver.

### 7. Logging & Tracing

Distributed tracing with Loguru and OpenTelemetry:

```python
# ContextVar-based trace propagation
from src.code_confluence_flow_bridge.logging.trace_utils import (
    trace_id_var,
    workflow_id_var,
    activity_name_var,
)

# Bind trace context to logger
log = seed_and_bind_logger_from_trace_id(
    trace_id=trace_id,
    workflow_id=workflow_id,
    workflow_run_id=run_id
)

# Logs include trace context automatically
log.info("Processing started", extra={"activity": "git_clone"})
```

Optional OTLP export to SigNoz when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.

### 8. Error Handling Pattern

Standardized error context for debugging:

```python
try:
    # Operation
except Exception as e:
    error_context = {
        "workflow_id": workflow_id,
        "activity_name": "process_git",
        "error_details": str(e),
        "traceback": traceback.format_exc(),
    }
    logger.error("Operation failed: {}", str(e), extra={"error_context": error_context})
    # Re-raise as ApplicationError for Temporal
    raise ApplicationError(str(e), type="CUSTOM_ERROR_TYPE") from e
```

## Key Directory Structure

```
src/code_confluence_flow_bridge/
├── main.py                          # FastAPI app, lifespan, endpoints
├── logging/
│   ├── log_config.py               # Loguru + OTLP setup
│   └── trace_utils.py              # ContextVar-based trace propagation
├── models/
│   ├── configuration/
│   │   └── settings.py             # EnvironmentSettings (all env vars)
│   ├── github/
│   │   └── github_repo.py          # Request/response models
│   ├── workflow/
│   │   └── repo_workflow_base.py   # Envelope models
│   └── code_confluence_parsing_models/
│       ├── unoplat_git_repository.py
│       ├── unoplat_package_manager_metadata.py
│       └── unoplat_file.py
├── processor/                      # Temporal workflows & activities
│   ├── repo_workflow.py            # Parent workflow orchestration
│   ├── codebase_child_workflow.py  # Child workflow for each codebase
│   ├── db/
│   │   ├── postgres/
│   │   │   ├── db.py              # AsyncEngine & session management
│   │   │   ├── parent_workflow_db_activity.py
│   │   │   ├── child_workflow_db_activity.py
│   │   │   └── framework_loader.py
│   │   └── graph_db/
│   │       ├── code_confluence_graph.py          # Neo4j connection
│   │       ├── code_confluence_graph_ingestion.py
│   │       └── code_confluence_graph_deletion.py
│   ├── git_activity/
│   │   ├── confluence_git_activity.py   # Clones repo activity
│   │   └── confluence_git_graph.py      # Inserts into Neo4j
│   ├── package_metadata_activity/       # Package extraction
│   └── activity_*.py                    # Interceptors for status updates
├── parser/
│   ├── generic_codebase_parser.py  # Main parser (delegates to processors)
│   ├── tree_sitter_*.py           # Tree-sitter utilities
│   ├── language_processors/
│   │   ├── base.py                # Abstract processor
│   │   ├── python_processor.py
│   │   └── typescript_processor.py
│   └── package_manager/
│       ├── package_manager_strategy.py
│       ├── package_manager_factory.py
│       └── detectors/              # Codebase detection
├── detector/
│   ├── base_detector.py
│   └── ripgrep_*.py               # Ripgrep-based detection
├── engine/
│   ├── framework_detection_service.py
│   ├── python/
│   │   └── python_framework_detection_service.py
│   └── generic_filters.py
└── github_app/
    └── router.py                   # GitHub App webhook endpoints
```

## Common Development Workflows

### Adding a New Framework

1. Add framework definition JSON to `framework-definitions/{language}/framework-name.json`
2. Validate: `task validate-single-framework FILE=...`
3. Framework loaded automatically at startup via `FrameworkDefinitionLoader`

### Implementing Language Support

1. Create `LanguageCodebaseProcessor` subclass in `parser/language_processors/`
2. Implement Tree-sitter extraction via `TreeSitterExtractorBase`
3. Register in `GenericCodebaseParser.LANGUAGE_PROCESSORS` mapping
4. Add detector (ripgrep-based) in `detector/`
5. Add to `main.py` lifespan detectors registration

### Testing Ingestion Locally

```bash
# Terminal 1: Start dependencies
task start-dependencies

# Terminal 2: Run development server
task run-dev

# Terminal 3: Submit test job
task run-client

# Monitor: Check Temporal UI at http://localhost:8081
```

### Debugging Workflows

1. Check Temporal UI for workflow execution history: http://localhost:8081
2. View Neo4j graph: http://localhost:7474 (default: neo4j/password)
3. Check PostgreSQL: `psql -U postgres -h localhost -d code_confluence`
4. Check logs with trace ID: Search for `trace_id` in logs

## Critical Implementation Notes

### Async/Await Best Practices

- Always use `async with` for database sessions
- Never use `.result()` on coroutines in sync context
- Use `asyncio.create_task()` for fire-and-forget background work (e.g., `monitor_workflow()`)
- ThreadPoolExecutor required for Temporal activities (can't run pure async code)

### Type Safety

- Use `type: ignore` for dynamic models from commons (Credentials, Repository, etc.)
- Enable strict type checking: `basedpyright typeCheckingMode = "strict"`
- Always define return types for activities (required by Temporal)

### Neo4j Transactions

- Always use `session.execute_write()` or `execute_read()` for managed transactions
- Don't use raw `session.run()` in activities (no retry)
- Batch operations with UNWIND for performance (see `codebase_parser_*_batch_size`)

### PostgreSQL Sessions

- Never commit manually in activity - use context manager
- Use `session.begin()` explicitly for transaction control
- Cascade deletes work via SQLAlchemy relationships

### Performance Optimization

- File batch processing: `CODEBASE_PARSER_FILE_BATCH_SIZE` (default 1000)
- Package batch processing: `CODEBASE_PARSER_PACKAGE_BATCH_SIZE` (default 500)
- Concurrent file parsing: `CODEBASE_PARSER_FILE_PROCESSING_CONCURRENCY` (default 3)
- Activity concurrency: `TEMPORAL_MAX_CONCURRENT_ACTIVITIES` (default 4)

## Environment Variables Summary

### Required at Startup
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `NEO4J_HOST`, `NEO4J_PORT`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- `TEMPORAL_SERVER_ADDRESS`

### Optional with Defaults
- `REPOSITORIES_BASE_PATH` → `~/.unoplat/repositories`
- `FRAMEWORK_DEFINITIONS_PATH` → `/framework-definitions`
- `LOG_LEVEL` → `DEBUG`
- `ALLOWED_ORIGINS` → `http://localhost:5173` (CORS)

### Feature Flags
- `OTEL_EXPORTER_OTLP_ENDPOINT` → Enable OpenTelemetry export
- `LOAD_FRAMEWORK_DEFINITIONS` → Load framework definitions at startup (default: true)
- `FRAMEWORK_DEFINITIONS_REQUIRED` → Fail startup if loading fails (default: false)
- `DB_ECHO` → Log all SQL (default: false)

## Integration with Commons

The project uses `unoplat-code-confluence-commons` for shared models:
- `Credentials` - Encrypted token storage
- `Repository`, `CodebaseConfig` - Repository metadata
- `RepositoryWorkflowRun`, `CodebaseWorkflowRun` - Workflow execution records
- `ProgrammingLanguageMetadata` - Language-specific config
- `Flag` - Feature flags

Reference via absolute imports: `from unoplat_code_confluence_commons.base_models import ...`

---

**Last Updated**: 2025-11-14
**Python Version**: 3.13+
**Package Manager**: uv

