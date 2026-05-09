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

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `e1d9b8966ae6d91f530e642d0fb01662c3cf2760` (2026-05-09). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync` (repo root; `pyproject.toml`)
### Build
- Not detected
### Dev
- `task run-query-engine-backend-dev` (repo root; `Taskfile.yml`)
### Test
- `task test` (repo root; `Taskfile.yml`)
### Lint
- `task lint` (repo root; `Taskfile.yml`)
### Type Check
- `task typecheck` (repo root; `Taskfile.yml`)

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This service is an AI-assisted codebase analysis and repository automation engine. It manages model/provider and tool credentials, launches Temporal workflows that inspect repositories, generate engineering and dependency guidance, validate framework usage, and produce/update AGENTS.md artifacts and pull requests. It also supports Codex OAuth, feedback submission, and feature flags for operating the agent runtime.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
