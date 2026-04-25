## Engineering Workflow
- Install: `task install` (config: `Taskfile.yml`).
- Test: `task test` (config: `Taskfile.yml`).

## Dependency Guide
- **Overview**: Full dependency descriptions are maintained in `dependencies_overview.md`.
- **Usage**: Keep this section concise and treat `dependencies_overview.md` as the source-of-truth dependency catalog.

## App Interfaces
- **Overview:** No app interface constructs have been documented for this codebase yet.
- **Inbound interfaces:** None documented.
- **Outbound interfaces:** None documented.
- **Internal interfaces:** None documented.
- **References:** See `app_interfaces.md` for the tracked interface inventory.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `a6db7131de30314e9053e74a395ac31be9cb767a` (2026-04-25). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync` (config: `pyproject.toml`).

### Build
- `uv build` (config: `pyproject.toml`).

### Dev
- Not detected.

### Test
- `uv run pytest -v tests/` (config: `pyproject.toml`).

### Lint
- `uv run ruff check .` (config: `ruff.toml`).

### Type Check
- `uv run --with mypy mypy src/unoplat_code_confluence_commons` (config: `pyproject.toml`).

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Logic Domain
- This codebase centers on a "code confluence" ingestion and analysis platform that stores repositories, codebases, source files, and workflow runs in PostgreSQL.
- Its core models capture Python and TypeScript structural signatures, detected data model spans, and framework feature metadata/query rules used to identify library usage across codebases.
- Supporting tables track agent execution events/snapshots, package manager and language metadata, credentials, flags, and AGENTS.md publication metadata.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
