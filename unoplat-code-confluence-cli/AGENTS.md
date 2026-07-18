<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `05234b1efe5762f633f9b3367f217c3b0fe2659b` (2026-07-15). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync --locked --group dev` — `pyproject.toml` / `uv.lock`

### Build
- `uv build` — `pyproject.toml`

### Dev
- `uv run ucc` — `pyproject.toml` (project script entry point)

### Test
- Not detected

### Lint
- `uv run --group dev ruff check src/` — `Taskfile.yml`

### Type Check
- `uv run --group dev pyrefly check src/` — `Taskfile.yml`

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

Unoplat Code Confluence CLI manages the Code Confluence platform’s local Docker Compose deployment, including versioned release manifests and the Flow Bridge, query engine, and frontend components. It registers and refreshes Git repositories for automated AGENTS.md generation, while checking repository-provider credentials and AI model-provider configuration and reporting application lifecycle results.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
