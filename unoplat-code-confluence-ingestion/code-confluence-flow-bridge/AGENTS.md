# AGENTS.md - Code Confluence Flow Bridge Agent Guide

## Engineering Workflow

- Install: `uv sync` (source: pyproject.toml, confidence: 0.9)
- Dev: `uv run fastapi dev` (source: Taskfile.yml, confidence: 0.45)
- Test: `uv run --group test pytest` (source: pyproject.toml, confidence: 0.6)
- Lint: `uv run ruff check src/` (source: ruff.toml, confidence: 0.9)
- Type check: `uv run --group dev basedpyright src/` (source: pyproject.toml, confidence: 0.8)

## Dependency Guide

- Package manager: `uv`.
- **sqlalchemy**: SQL toolkit + ORM. Use Core for SQL expressions, schema/transaction services, and ORM for object persistence and queries.
- **opentelemetry-exporter-otlp**: OTLP exporter bundle (gRPC + HTTP/protobuf). Install when you want a single dependency for OTLP export, then pick a specific protocol package for leaner builds.
- **gql**: GraphQL client built on graphql-core. Execute queries/mutations/subscriptions over HTTP or WebSocket with sync/async APIs and schema validation.
- **temporalio**: Temporal Python SDK. Use client/worker modules to connect to a Temporal cluster and run workflows/activities with data conversion/testing helpers.
- **opentelemetry-sdk**: OpenTelemetry SDK implementation. Configure providers/processors/exporters and pair with API + instrumentation to emit traces/metrics/logs.
- **greenlet**: Lightweight, cooperatively scheduled coroutines. Use to manage in-thread context switching and bridge async flows to synchronous style.
- **pydantic**: Typed data validation/serialization. Define models with type hints, validate/coerce inputs, and emit JSON Schema.
- **requirements-parser**: Parse pip requirements files. Inspect names, specifiers, extras, and VCS/URL entries without filesystem traversal.
- **aiofile**: Async file I/O. Use async_open and reader/writer helpers for chunked async reads/writes across backends.
- **tree-sitter-language-pack**: Bundled Tree-sitter languages. Use get_binding/get_language/get_parser to access parsers without manual compilation.
- **tomlkit**: Style-preserving TOML parser/editor. Maintain comments and formatting when updating TOML configs.
- **packaging**: Packaging interoperability utilities. Parse versions/specifiers/markers/tags/requirements consistently.
- **opentelemetry-instrumentation-logging**: Logging integration. Inject trace/span context via a LogRecord factory or LoggingInstrumentor.
- **tiktoken**: Fast BPE tokenizer for OpenAI models. Load model encodings to encode/decode token IDs.
- **asyncpg**: Async PostgreSQL client. Use pools, transactions, prepared statements, and rich type conversion via asyncio.
- **psycopg2-binary**: Prebuilt Psycopg 2 adapter. DB-API 2.0 access with libpq-backed performance and no local compilation.
- **pygithub**: GitHub REST API client. Use Github entrypoint to manage repos, users, and org resources.
- **typing-extensions**: Backported typing features. Keep type hints compatible with older Python versions and experimental PEPs.
- **grpcio**: gRPC runtime. Define services via Protocol Buffers and run HTTP/2 RPC servers/clients.
- **sqlmodel**: SQL + Pydantic models. Define typed models that map to SQL tables with SQLAlchemy compatibility.
- **pydantic-settings**: Settings loader for env/.env/secrets. Define BaseSettings models and configure sources.
- **validate-pyproject**: Validate pyproject.toml via JSON Schema. Use CLI or API for schema checks.
- **passlib**: Password hashing toolkit. Manage hash schemes and verification with CryptContext.
- **fastapi**: Async API framework. Use type hints, OpenAPI/JSON Schema, and auto docs for HTTP services.
- **loguru**: Structured logging. Use the pre-configured logger and add sinks with `logger.add()`.
- **pyyaml**: YAML parser/emitter. Load/dump YAML with high-level APIs or low-level event interfaces.
- **opentelemetry-api**: OpenTelemetry API layer. Use abstract/no-op interfaces and pair with SDK for actual telemetry.
- **gitpython**: Git repository access. Interact with git objects and operations programmatically.

## Business Logic Domain

- This service ingests Git repositories, detects codebases/packages/files, and extracts structural signatures, imports, and package-manager dependencies across languages.
- Workflow models capture repository/codebase processing runs, orchestration state, error reporting, and issue feedback used for monitoring and follow-up actions.
- GitHub App integration models support manifest generation, installation onboarding, and repository refresh requests with captured API metadata.
- Key data structures and schemas (parsing, workflow tracking, GitHub integration) are cataloged in `business_logic_references.md`.

## App Interfaces

- **FastAPI HTTP endpoints** live in `src/code_confluence_flow_bridge/main.py`, `src/code_confluence_flow_bridge/github_app/router.py`, and `src/code_confluence_flow_bridge/routers/github_issues/router.py`.
- Ingestion/admin endpoints cover token management (`/ingest-token`, `/update-token`, `/delete-token`), repository lifecycle (`/start-ingestion`, `/repository-status`, `/repository-data`, `/refresh-repository`, `/delete-repository`), and metadata access (`/codebase-metadata`, `/parent-workflow-jobs`, `/get/ingestedRepositories`).
- Feature flag and user lookup routes are `/flags`, `/flags/{flag_name}`, and `/user-details`.
- GitHub App integration exposes `/app-manifest`, `/app-manifest/callback`, and `/webhook`.
- Issue feedback endpoints live under the GitHub issues router (`/issues`, `/feedback`).
- Detailed interface inventory with response models is maintained in `app_interfaces.md`.

## Build/Lint/Test Commands

```bash
# Development
task dev                          # Start dependencies + run FastAPI
task sync                         # Install dependencies with uv

# Testing
task test                         # Run all tests with coverage
uv run --group test pytest tests/path/to/test_file.py::test_function_name  # Single test

# Code Quality
task lint                         # Run ruff linter
task lint-fix                     # Auto-fix lint issues
task typecheck                    # Run basedpyright type checker
task format                       # Format code with ruff
task code-quality                 # Run all checks (lint + typecheck + schema validation)
```

## Code Style Guidelines

**Imports**: Absolute imports only (no relative). Use top-level imports. Ruff enforces: I, F401, F403, F405, TID (ban-relative-imports). Order: future, standard-library, third-party, first-party, local-folder.

**Formatting**: Line length 88. Use `uv run ruff format` - never fix import order manually. Python >=3.13 required.

**Types**: Always define precise types. No `Any` types. Use basedpyright strict mode. For Pydantic JSON: use `model_dump_json()` not manual serialization.

**Naming**: Follow Python PEP 8. Use descriptive names. Avoid nested functions (not preferred in this codebase).

**Error Handling**: Use `@logger.catch` decorator. PostgreSQL sessions: use `session.begin()` but yield `AsyncSession` for automatic transactions.

**Logging**: Use Loguru's native formatting `logger.info("msg {}", var)` NOT f-strings `logger.info(f"msg {var}")`. For expensive ops: `logger.opt(lazy=True).debug("Result: {}", lambda: expensive_fn())`. Context injection arg `ctx` excluded from docstrings (Google format).

**Database**: All Postgres operations auto-transactional via `session.begin()`. Use asyncpg for async operations.

**Testing**: Use `uv run --group test pytest` for tests. Mark integration tests with `@pytest.mark.integration`. Session-scoped fixtures for async.

**Dependencies**: Use `uv` commands exclusively. Test dependencies in `[dependency-groups]` section. Activate shell: `uv run python`.

## Implementation Workflow

**API Verification**: Before implementing framework/library features, verify API methods with official documentation using Context7 tool.

**Post-Implementation**: ALWAYS run `task typecheck` after implementation. Fix all type errors before considering work complete.
