# AGENTS.md - Code Confluence Flow Bridge Agent Guide

## Build/Lint/Test Commands

```bash
# Install
uv sync

# Development
uv run fastapi dev

# Testing
uv run --python 3.13 --group test pytest --cov=src/code_confluence_flow_bridge --cov-report=html:coverage_reports tests/ -v
uv run --group test pytest tests/path/to/test_file.py::test_function_name  # Single test

# Lint
uv run ruff check src/

# Type check
uv run --group dev basedpyright src/
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

## Business Domain Context

This service ingests and analyzes GitHub repositories and codebases, capturing file-level structural signatures, dependency metadata, and package manager details to build a consolidated “code confluence” representation. It models repository and codebase workflows, tracking ingestion and agent-processing runs with statuses, error reports, and issue feedback, alongside GitHub App manifest registration flows.

Key models live under:
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/`
- `src/code_confluence_flow_bridge/models/github/`
- `src/code_confluence_flow_bridge/models/workflow/`
- `src/code_confluence_flow_bridge/github_app/models.py`
- `src/code_confluence_flow_bridge/models/configuration/settings.py`
- `src/code_confluence_flow_bridge/engine/programming_language/python/python_source_context.py`
- `src/code_confluence_flow_bridge/parser/`

## Inbound Interfaces

FastAPI endpoints are defined in:
- `src/code_confluence_flow_bridge/main.py` (ingestion, repository data, flags, metadata)
- `src/code_confluence_flow_bridge/github_app/router.py` (GitHub App manifest + webhook)
- `src/code_confluence_flow_bridge/routers/github_issues/router.py` (issue tracking/feedback)

## Key Dependencies

- OpenTelemetry: `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp`, `opentelemetry-instrumentation-logging`
- Temporal workflows: `temporalio`
- API framework: `fastapi`
- Data validation/settings: `pydantic`, `pydantic-settings`
- Database: `sqlalchemy`, `sqlmodel`, `asyncpg`, `psycopg2-binary`
- Logging: `loguru`
- Parsing/tooling: `tree-sitter-language-pack`, `pyyaml`, `tomlkit`, `requirements-parser`

## Implementation Workflow

**API Verification**: Before implementing framework/library features, verify API methods with official documentation using Context7 tool.

**Post-Implementation**: ALWAYS run `task typecheck` after implementation. Fix all type errors before considering work complete.
