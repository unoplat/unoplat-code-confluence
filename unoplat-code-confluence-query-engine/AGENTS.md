# Agent Guidelines

## Engineering Workflow
- **Install**: `task sync` (from `Taskfile.yml`)
- **Dev**: `task run-query-engine-backend-dev` (from `Taskfile.yml`)
- **Test**: `task test` (from `Taskfile.yml`)
- **Lint**: `task lint` (from `Taskfile.yml`)
- **Type check**: `task typecheck` (from `Taskfile.yml`)

## Dependency Guide
- **Overview**: Full dependency descriptions are maintained in `dependencies_overview.md`.
- **Usage**: Keep this section concise and treat `dependencies_overview.md` as the source-of-truth dependency catalog.

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

## Architecture
See [`architecture.md`](./architecture.md) for the current validated Mermaid architecture diagram when external interfaces are detected.

## Commands
- **Test all**: `task test` (starts deps, runs tests with coverage, stops deps)
- **Test single**: `uv run --group test pytest tests/path/to/test_file.py::test_function_name -v`
- **Lint**: `task lint` (check) or `task lint-fix` (auto-fix)
- **Format**: `task format` (ruff formatter)
- **Type check**: `task typecheck` (pyrefly strict preset)
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

## Backlog Workflow

This project uses Backlog.md MCP for all task and project management. Before creating tasks or tracking work, read [`backlog_instructions.md`](./backlog_instructions.md) for the complete workflow guidance.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `5ecdba39d57f50c5188a8e32b9dd4f52d01611fe` (2026-07-18). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `task sync` (repo root; `Taskfile.yml` -> `uv sync`)
### Build
- Not detected
### Dev
- `task run-query-engine-backend-dev` (repo root; `Taskfile.yml` -> `uv run fastapi dev --port 8001` in `src/unoplat_code_confluence_query_engine`)
### Test
- `task test` (repo root; `Taskfile.yml` -> starts dependencies, runs `uv sync --group test`, then `uv run --python 3.13 --group test pytest --cov=src/unoplat_code_confluence_query_engine --cov-report=html:coverage_reports tests/ -v`)
### Lint
- `task lint` (repo root; `Taskfile.yml` -> `uv run --group dev ruff check src/`)
### Type Check
- `task typecheck` (repo root; `Taskfile.yml` -> `uv run --group dev pyrefly check src/`)

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This service is an AI-assisted codebase analysis and repository automation engine. It manages model/provider and tool credentials, launches Temporal workflows that inspect repositories, generate engineering and dependency guidance, validate framework usage, and produce/update AGENTS.md artifacts and pull requests. It also supports Codex OAuth, feedback submission, and feature flags for operating the agent runtime.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

## Architecture
See [`architecture.md`](./architecture.md) for the canonical system architecture diagram.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
