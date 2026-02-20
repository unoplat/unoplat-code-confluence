# Agent Guidelines

## Engineering Workflow
- **Install**: `task sync` (from `Taskfile.yml`)
- **Dev**: `task run-query-engine-backend-dev` (from `Taskfile.yml`)
- **Test**: `task test` (from `Taskfile.yml`)
- **Lint**: `task lint` (from `Taskfile.yml`)
- **Type check**: `task typecheck` (from `Taskfile.yml`)

## Dependency Guide
- **Package management**: Use `uv` with `pyproject.toml` for installing and syncing dependencies.
- **aiopath**: Async pathlib for Python: a complete reimplementation of Python’s pathlib that is compatible with asyncio, trio, and async/await, with all I/O performed asynchronously and awaitably. Usage: use `AsyncPath`/`AsyncPurePath` with familiar pathlib APIs, and await I/O methods like read/write/open or async globbing that return async-friendly results.
- **qs-codec**: Query string encoding and decoding library for Python, ported from qs for JavaScript. Usage: encode/decode nested dict/list structures with list formats (indices, brackets, repeat, comma), dot-notation, charset options, hooks, and null/safety handling.
- **sqlalchemy**: SQL toolkit and ORM for Python providing comprehensive database tools. Usage: rely on Core for composable SQL expressions and the ORM for object mappings, unit-of-work persistence, and object-centric querying.
- **asyncpg**: Async PostgreSQL client designed for asyncio. Usage: use the native protocol API for connections, transactions, prepared statements, cursors, pooling, and rich PostgreSQL type conversions.
- **loguru**: Pre-instanced logger that simplifies Python logging. Usage: emit logs with the global `logger`, add sinks via `logger.add()`, and configure levels or formatting as needed.
- **sse-starlette**: Server-Sent Events implementation for Starlette/FastAPI following the W3C SSE spec. Usage: stream async event generators with `EventSourceResponse`, using helpers like `ServerSentEvent`/`JSONServerSentEvent` and disconnect handling.
- **ghapi**: Pythonic interface to GitHub’s OpenAPI spec with always-updated coverage. Usage: call GitHub endpoints as standard Python methods with docs/autocomplete, or use the CLI for scripting.
- **sqlmodel**: SQLModel for relational database access with Python objects. Usage: define models with modern type annotations that serve as ORM mappings and Pydantic validation, while accessing underlying SQLAlchemy features.
- **fastapi**: High-performance API framework built on type hints. Usage: declare routes with automatic validation/OpenAPI docs and dependency injection for rapid API development.
- **logfire**: Observability platform built on OpenTelemetry with strong Python support. Usage: initialize with `logfire.configure()` and use instrumentation helpers like `logfire.instrument_<package>()` for traces, logs, and metrics.
- **pydantic-ai-slim**: Minimal core for Pydantic AI. Usage: install the slim core and add only the provider/tool extras you need to keep dependencies lightweight.
- **aiofiles**: Async file I/O library for asyncio. Usage: use async file APIs mirroring standard file objects while delegating blocking work to a thread pool.
- **pydantic-ai**: Python agent framework for production-grade generative AI workflows. Usage: build type-safe, model-agnostic agents with structured outputs, tool calls, and streaming/observability support.

## Business Logic Domain
- **Overview**: AI-driven codebase analysis service that orchestrates repository workflows to generate structured documentation outputs and track execution across codebases.
- **Core data focus**: Provider configuration (including OAuth flows), model parameters/catalogs, tool/MCP server setup, repository rulesets/metadata, and agent runtime dependencies.
- **Workflow telemetry**: Agent events, workflow envelopes, and usage/cost statistics capture lifecycle and execution monitoring.
- **Structured outputs**: Typed schemas for agent markdown responses, AGENTS.md updates, engineering workflows, and business logic summaries.
- **Primary references**: See `business_logic_references.md` for the source-of-truth module map.

## App Interfaces
- **Protocol**: FastAPI HTTP endpoints under `src/unoplat_code_confluence_query_engine/api/v1/endpoints`.
- **Surface area**: Model configuration + provider/OAuth flows, feature flag CRUD, repository agent rules/snapshots/markdown PR endpoints, and tool configuration management.
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
