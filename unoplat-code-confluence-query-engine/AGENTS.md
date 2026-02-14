# Agent Guidelines

## Engineering Workflow
- **Install**: `uv sync` (from `pyproject.toml`)
- **Install (tests)**: `uv sync --group test` (from `pyproject.toml`)
- **Dev**: `uv run fastapi dev --port 8001` (from `Taskfile.yml`)
- **Test**: `uv run --python 3.13 --group test pytest --cov=src/unoplat_code_confluence_query_engine --cov-report=html:coverage_reports tests/ -v` (from `Taskfile.yml`)
- **Lint**: `uv run --group dev ruff check src/` (from `ruff.toml`)
- **Type check**: `uv run --group dev basedpyright src/` (from `pyproject.toml`)

## Dependency Guide
- **Package management**: Use `uv` with `pyproject.toml` for installing and syncing dependencies.
- **sqlmodel**: SQLModel is a library for interacting with SQL (relational) databases from Python code using Python objects, designed to be intuitive, easy to use, highly compatible, and robust. Usage: define ORM models that combine SQLAlchemy-style mappings with Pydantic-style validation via type annotations.
- **sse-starlette**: Production-ready Server-Sent Events implementation for Starlette and FastAPI following the W3C SSE specification. Usage: stream async generator output with `EventSourceResponse` and `ServerSentEvent` helpers, including graceful disconnect handling.
- **sqlalchemy**: Python SQL toolkit and ORM for comprehensive database integration. Usage: use Core for composable SQL expressions/transactions and ORM for mapping Python objects and relationships.
- **aiofiles**: Async file I/O library for asyncio applications. Usage: use async file APIs that mirror standard file objects to avoid blocking the event loop.
- **pydantic-ai**: Pydantic AI framework for production-grade agent workflows. Usage: build model-agnostic agents with Pydantic-validated outputs and dependency-injected tools, plus streaming and orchestration support.
- **fastapi**: High-performance web framework built on type hints. Usage: define API routes with automatic OpenAPI docs, validation, and dependency injection.
- **loguru**: Simplified logging with a preconfigured global logger. Usage: emit logs via `logger` and add sinks with `logger.add()` for custom formats and levels.
- **asyncpg**: Async PostgreSQL client for asyncio. Usage: use native protocol features like prepared statements, cursors, and pools for high-performance access.
- **pydantic-ai-slim**: Pydantic AI core logic with minimal dependencies. Usage: install slim core and add provider-specific extras (openai, anthropic, google) as needed.
- **logfire**: Observability SDK built on OpenTelemetry. Usage: configure Logfire and instrument services to emit traces, metrics, and logs.
- **qs-codec**: Query string encoder/decoder for nested data. Usage: serialize/parse nested dict/list structures with configurable formats and decoding options.
- **aiopath**: Async `pathlib` compatible with asyncio. Usage: use awaitable filesystem operations, async globbing, and async iterators for path traversal.

## Business Logic Domain
- **Overview**: AI-driven codebase analysis/query engine that orchestrates repository workflows, captures agent progress and outputs, and persists snapshots plus usage statistics.
- **Core data focus**: Configuration of LLM providers (including OAuth flows), tool/MCP integrations, repository rulesets, and runtime dependencies for agent execution.
- **Structured outputs**: Business logic domains, interfaces, and engineering workflow results are modeled for downstream reporting.
- **Primary references**: See `business_logic_references.md` for the source-of-truth module map.

## App Interfaces
- **Protocol**: FastAPI HTTP endpoints under `src/unoplat_code_confluence_query_engine/api/v1/endpoints`.
- **Surface area**: Model configuration + provider/OAuth flows, feature flag CRUD, repository agent rule snapshots, and tool configuration management.
- **Reference map**: See `app_interfaces.md` for endpoint-to-module details.

## Commands
- **Test all**: `task test` (starts deps, runs tests with coverage, stops deps)
- **Test single**: `uv run --group test pytest tests/path/to/test_file.py::test_function_name -v`
- **Lint**: `task lint` (check) or `task lint-fix` (auto-fix)
- **Format**: `task format` (ruff formatter)
- **Type check**: `task typecheck` (basedpyright strict mode)
- **Dev server**: `task run-query-engine-backend-dev` (port 8001)

## Code Style
- **Imports**: Absolute only (no relative), use ruff for ordering (`task lint-fix`)
- **Types**: Always precise types - never use `Any`, use `typing` module generics
- **Functions**: No nested functions - keep flat structure at module level
- **Pydantic**: Use `model_dump_json()` for JSON serialization (not `json.dumps`)
- **Docstrings**: Google format, omit `ctx` param (dependency injection magic)
- **Sessions**: Always `session.begin()` but yield `AsyncSession` for auto-transactions
- **Error handling**: Use structured exceptions, add proper context/trace IDs
- **Tool verification**: Use context7 tool to verify API methods before implementation
- **Python commands**: Always use `uv run --group <group>` (e.g., `--group test` for tests)


## Caveats
1. When a shell command fails with "failed in sandbox", use the permission request tool (with 'with_escalated_permissions") to ask the user for approval before
retrying.
2. always when want to run python script open shell with 'uv run python'.

## BACKLOG WORKFLOW INSTRUCTIONS

This project uses Backlog.md MCP for all task and project management activities.

**CRITICAL GUIDANCE**

- If your client supports MCP resources, read `backlog://workflow/overview` to understand when and how to use Backlog for this project.
- If your client only supports tools or the above request fails, call `backlog.get_workflow_overview()` tool to load the tool-oriented overview (it lists the matching guide tools).

- **First time working here?** Read the overview resource IMMEDIATELY to learn the workflow
- **Already familiar?** You should have the overview cached ("## Backlog.md Overview (MCP)")
- **When to read it**: BEFORE creating tasks, or when you're unsure whether to track work

These guides cover:
- Decision framework for when to create tasks
- Search-first workflow to avoid duplicates
- Links to detailed guides for task creation, execution, and completion
- MCP tools reference

You MUST read the overview resource to understand the complete workflow. The information is NOT summarized here.
