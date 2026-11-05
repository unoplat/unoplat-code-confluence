# AGENTS.md - Code Confluence Flow Bridge Agent Guide

## Code Style Guidelines

**Imports**: Absolute imports only (no relative). Use top-level imports. Ruff enforces: I, F401, F403, F405, TID (ban-relative-imports). Order: future, standard-library, third-party, first-party, local-folder.

**Formatting**: Line length 88. Use `uv run ruff format` - never fix import order manually. Python >=3.13 required.

**Types**: Always define precise types. No `Any` types. Use pyrefly strict preset. For Pydantic JSON: use `model_dump_json()` not manual serialization.

**Naming**: Follow Python PEP 8. Use descriptive names. Avoid nested functions (not preferred in this codebase).

**Error Handling**: Use `@logger.catch` decorator. PostgreSQL sessions: use `session.begin()` but yield `AsyncSession` for automatic transactions.

**Logging**: Use Loguru's native formatting `logger.info("msg {}", var)` NOT f-strings `logger.info(f"msg {var}")`. For expensive ops: `logger.opt(lazy=True).debug("Result: {}", lambda: expensive_fn())`. Context injection arg `ctx` excluded from docstrings (Google format).

**Database**: All Postgres operations auto-transactional via `session.begin()`. Use asyncpg for async operations.

**Testing**: Use `uv run --group test pytest` for tests. Mark integration tests with `@pytest.mark.integration`. Session-scoped fixtures for async.

**Dependencies**: Use `uv` commands exclusively. Test dependencies in `[dependency-groups]` section. Activate shell: `uv run python`.

## Implementation Workflow

**API Verification**: Before implementing framework/library features, verify API methods with official documentation using Context7 tool.

**Post-Implementation**: ALWAYS run `task typecheck` after implementation. Fix all type errors before considering work complete.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `a5948971aedbc9c28b0f70964454c7f6a7c4d6da` (2026-08-31). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync` (working directory: `.`, config: `pyproject.toml`)
### Build
- Not detected
### Dev
- `task dev` (working directory: `.`, config: `Taskfile.yml`; starts dependencies and the FastAPI app)
### Test
- `task test` (working directory: `.`, config: `Taskfile.yml`; syncs the test dependency group and runs pytest with coverage)
### Lint
- `uv run ruff check src/` (working directory: `.`, config: `ruff.toml`)
### Type Check
- `uv run --group dev pyrefly check src/` (working directory: `.`, config: `pyproject.toml`)

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This service centers on repository ingestion and code intelligence for GitHub projects. It parses Python and TypeScript code, extracts imports and structural signatures, detects package managers and workspace layouts, and packages repository/codebase metadata for downstream processing. It also tracks Temporal workflow state, GitHub App onboarding, and issue/feedback submission around that ingestion pipeline.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
