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

> Generated from branch `dev` at commit `a6db7131de30314e9053e74a395ac31be9cb767a` (2026-04-25). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync --group dev --group test` (repo root; config: `Taskfile.yml`)
### Build
- Not detected
### Dev
- `CODE_CONFLUENCE_BRIDGE_URL=http://localhost:8000 TOKEN_ENCRYPTION_KEY=0PiVvlu6HExNWkYjukuG0CAV930B4OsqXNPItAvsxhQ= MCP_SERVERS_CONFIG_PATH=../../mcp-servers.json CODEX_OPENAI_CALLBACK_PORT=1455 CODEX_OPENAI_REDIRECT_URI=http://localhost:1455/auth/callback uv run fastapi dev --port 8001` (working directory: `src/unoplat_code_confluence_query_engine`; config: `Taskfile.yml`)
### Test
- `uv run --python 3.13 --group test pytest --cov=src/unoplat_code_confluence_query_engine --cov-report=html:coverage_reports tests/ -v` (repo root; config: `Taskfile.yml`)
### Lint
- `uv run --group dev ruff check src/` (repo root; config: `Taskfile.yml`)
### Type Check
- `uv run --group dev basedpyright src/` (repo root; config: `Taskfile.yml`)

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Logic Domain
- **Overview**: AI-assisted codebase analysis and repository workflow orchestration for generating structured documentation, AGENTS.md updates, and validation outputs.
- **Core data focus**: AI provider/model configuration, OAuth and tool/MCP setup, repository metadata/rulesets, Temporal agent dependencies, workflow envelopes, event telemetry, and usage statistics.
- **Artifacts**: Canonical outputs include engineering workflows, dependency guides, business-domain summaries, and framework-feature validation records.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
