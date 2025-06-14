# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
# Install dependencies (requires uv package manager)
uv sync

# Sync test dependencies
uv sync --group test
```

### Running the Application

```bash
# Start all required services and run in development mode
task dev

# Or start services individually:
task start-temporal      # Start Temporal server (port 8080)
task start-neo4j        # Start Neo4j graph database
task start-dependencies # Start all dependencies via docker-compose
task run-dev           # Run FastAPI in development mode

# Run the CLI client to submit a job
task run-client
```

### Testing

```bash
# Run all tests with coverage
task test

# Run tests in CI mode (using act)
task ci-test

# Generate test prerequisites (required before running tests)
task generate-test-prerequisites
```

### Code Quality

```bash
# Run linting with ruff (configured in ruff.toml)
uv run ruff check src/

# Run type checking
uv run mypy src/

# Format code
uv run ruff format src/
```

### Package Management

```bash
# Update a specific package
task update-package PACKAGE=package_name

# Update all packages
task update-all-packages
```

## Architecture Overview

### Core Components

1. **FastAPI Application** (`src/code_confluence_flow_bridge/main.py`)
   - REST API for repository ingestion and status monitoring
   - Manages GitHub authentication tokens
   - Initiates Temporal workflows for processing

2. **Temporal Workflows**
   - **RepoWorkflow** (`processor/repo_workflow.py`): Parent workflow that orchestrates repository processing
   - **CodebaseChildWorkflow** (`processor/codebase_child_workflow.py`): Child workflows for processing individual codebases within a repository

3. **Activities**
   - **GitActivity**: Clones and analyzes Git repositories
   - **CodebaseProcessingActivity**: Processes codebase using tree-sitter for AST analysis
   - **PackageMetadataActivity**: Extracts package manager metadata
   - **Database Activities**: Handle PostgreSQL and Neo4j persistence

4. **Parsers**
   - **Language Parsers**: Currently supports Python with tree-sitter
   - **Package Manager Parsers**: Support for pip, poetry, and uv
   - **Linter Integration**: Ruff strategy for Python linting

### Data Flow

1. User submits GitHub repository via `/start-ingestion` endpoint
2. Main FastAPI app creates a Temporal workflow with trace ID
3. RepoWorkflow:
   - Clones repository via GitActivity
   - Inserts repository metadata into Neo4j graph
   - Spawns child workflows for each detected codebase
4. CodebaseChildWorkflow:
   - Extracts package metadata
   - Processes code structure using tree-sitter
   - Stores results in both PostgreSQL and Neo4j

### Key Design Patterns

- **Envelope Pattern**: All workflow/activity parameters wrapped in envelope models for type safety
- **Interceptors**: Custom Temporal interceptors for workflow status tracking and logging
- **Factory Pattern**: Used for parser selection (codebase, package manager, linter)
- **Strategy Pattern**: Different strategies for package managers and linters

### Model Architecture

**Current State**: All models are being consolidated into `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/`

**Legacy Models (Being Deprecated)**:
- `src/code_confluence_flow_bridge/models/chapi/` - Legacy Chapi AST models
- `src/code_confluence_flow_bridge/models/chapi_forge/` - Legacy domain models 

**Migration Notes**:
- Use models from `code_confluence_parsing_models` for all new development
- Legacy `chapi/` and `chapi_forge/` directories will be removed after refactoring
- Some legacy components (like SetupParser) may still reference old models during transition

## Temporal Workflow Architecture

### Worker Configuration

The Temporal worker (`main.py:run_worker`) is configured with:
- **Task Queue**: `unoplat-code-confluence-repository-context-ingestion`
- **Thread Pool**: Sized as `max_concurrent_activities + 4` for optimal performance
- **Autoscaling Support**: Optional poller autoscaling for dynamic workload handling
- **Interceptors**: Custom interceptors for status tracking and activity monitoring

### Workflow Patterns

1. **Parent-Child Workflow Pattern**
   - `RepoWorkflow` spawns multiple `CodebaseChildWorkflow` instances
   - Uses `ParentClosePolicy.TERMINATE` to ensure child workflows are cleaned up
   - Child workflows run independently for each codebase in a repository

2. **Activity Execution**
   - All activities use `ActivityRetriesConfig.DEFAULT` retry policy
   - Activities are executed with appropriate timeouts (typically 10 minutes)
   - Thread pool executor handles concurrent activity execution

3. **Workflow Sandbox**
   - Uses `workflow.unsafe.imports_passed_through()` for external module imports
   - Ensures workflow determinism by controlling imports

### Activity Design

Activities follow these patterns:
- Accept envelope models as parameters for type safety
- Return domain models (e.g., `UnoplatGitRepository`, `UnoplatPackageManagerMetadata`)
- Handle errors with structured error contexts including workflow IDs and trace IDs
- Use `@activity.defn` decorator for registration

## Neo4j Graph Database Integration

### Neomodel Configuration

- **Connection**: Managed through `CodeConfluenceGraphIngestion` class
- **Async Support**: Uses `AsyncDatabase` for non-blocking operations
- **Connection String**: `bolt://username:password@host:port`

### Graph Model Structure

The codebase uses neomodel's `StructuredNode` and `StructuredRel` for defining:

1. **Node Types**:
   - Repository nodes
   - Package nodes
   - Module/File nodes
   - Function/Class nodes
   - Import nodes

2. **Relationship Types**:
   - `HAS_PACKAGE`: Repository to Package
   - `HAS_MODULE`: Package to Module
   - `IMPORTS`: Module to Module
   - `CONTAINS`: Module to Function/Class
   - `CALLS`: Function to Function

3. **Relationship Properties**:
   - Use `StructuredRel` subclasses for relationship metadata
   - Properties like `since`, `version`, `type` on relationships

### Query Patterns

Common neomodel query patterns used:
```python
# Basic node creation
node = MyNode(property=value).save()

# Relationship creation
node1.relationship.connect(node2, {'property': value})

# Querying with filters
MyNode.nodes.filter(property__gt=value)

# Traversing relationships
MyNode.nodes.traverse_relations(path="relationship__nested_relationship")

# Fetch relations for performance
MyNode.nodes.fetch_relations('relationship').all()
```

### Transaction Management

- Uses context managers for transaction boundaries
- Automatic rollback on exceptions
- Batch operations with `create_or_update()` for efficiency

## Database Schema

### PostgreSQL Schema
Stores workflow execution data:
- **Repository**: Repository configurations
- **RepositoryWorkflowRun**: Parent workflow execution status
- **CodebaseWorkflowRun**: Child workflow execution status
- **Credentials**: Encrypted GitHub tokens
- **Flag**: Feature flags

### Neo4j Schema
Stores code structure graph:
- Nodes represent code entities (packages, modules, functions)
- Relationships represent dependencies and structure
- Properties store metadata (versions, types, parameters)
- **Detailed schema documentation**: See `schema_documentation.md` for complete node and relationship definitions
- **Recent Changes**: `CodeConfluenceCodebase` now supports multiple root packages via `ArrayProperty(StringProperty())` instead of single `local_path`, and includes `codebase_path` for the base directory

## Environment Variables

Key environment variables (see `main.py:run-dev` task for defaults):
- `TEMPORAL_SERVER_ADDRESS`: Temporal server location
- `DB_HOST/PORT/USER/PASSWORD/NAME`: PostgreSQL configuration  
- `NEO4J_HOST/PORT/USERNAME/PASSWORD`: Neo4j configuration
- `UNOPLAT_TEMPORAL_MAX_CONCURRENT_ACTIVITIES`: Worker concurrency settings
- `UNOPLAT_TEMPORAL_ENABLE_POLLER_AUTOSCALING`: Enable autoscaling pollers

## Error Handling

### Temporal Error Handling
- Activities throw `ApplicationError` with specific error types
- Retry policies handle transient failures
- Workflow interceptors track failure states

### Standardized Error Context
All errors include:
- `workflow_id`: Temporal workflow identifier
- `activity_name`: Failed activity name
- `error_details`: Error message
- `traceback`: Full stack trace
- Additional context (repository, codebase, etc.)

### GitHub Issue Integration
- `/code-confluence/issues` endpoint creates GitHub issues for errors
- Issues are tracked in database with workflow runs
- Automatic error reporting to unoplat/unoplat-code-confluence repository

## Security Considerations

- **Token Encryption**: GitHub tokens encrypted with Fernet before storage
- **Environment Variables**: All sensitive configuration via environment
- **Bearer Authentication**: Token management endpoints require authentication
- **Database Credentials**: Stored securely in environment variables

## Development Tips

1. **Temporal Workflow Development**:
   - Always use envelope models for workflow/activity parameters
   - Import external modules within `workflow.unsafe.imports_passed_through()`
   - Use structured logging with trace IDs for debugging
   - Test workflows with time-skipping test environment

2. **Neo4j/Neomodel Development**:
   - Use `fetch_relations()` to avoid N+1 queries
   - Leverage `create_or_update()` for idempotent operations
   - Use transactions for multi-step operations
   - Define indexes on frequently queried properties

3. **Testing**:
   - Mock Temporal workflows/activities in unit tests
   - Use test databases for integration tests
   - Generate test prerequisites with `task generate-test-prerequisites`
   - Coverage reports available in `coverage_reports/`

4. **Asyncio and SSE Development**:
   - **Follow asyncio best practices**: See `asyncio-practices.md` for comprehensive guidelines
   - Avoid double-threading anti-pattern (no `threading.Timer` in ThreadPoolExecutor)
   - Use `asyncio.run_coroutine_threadsafe()` for thread-safe communication
   - Always use bounded queues (`asyncio.Queue(maxsize=100)`) for backpressure
   - Replace `threading.Timer` with `asyncio.create_task()` and `asyncio.sleep()`
   - Use Python 3.12's eager task execution for performance gains
   - **AVOID NESTED FUNCTIONS**: Do not define functions inside other functions, especially in async contexts. This causes mypy issues with context managers and async/sync mixing. Always define helper functions at module level.