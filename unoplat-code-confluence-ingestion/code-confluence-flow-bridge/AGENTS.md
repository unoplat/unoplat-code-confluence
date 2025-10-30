# AGENTS.md - Code Confluence Flow Bridge Agent Guide

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
