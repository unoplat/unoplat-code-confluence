<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `57d1d23304bfc4e45c00dae712eec11747f33c0d` (2026-07-24). Content may become stale as new commits land.

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

Unoplat Code Confluence CLI manages a local Docker Compose deployment for repository-aware AI code assistance, including Flow Bridge, a query engine, and a frontend. It registers and refreshes Git repositories, verifies repository and model-provider credentials, tracks GitHub release manifests and installed state, and initiates AGENTS.md-generation workflows that raise pull requests.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

## Architecture
See [`architecture.md`](./architecture.md) for the canonical system architecture diagram.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
