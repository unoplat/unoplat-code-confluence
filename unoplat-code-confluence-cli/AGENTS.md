<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `5ecdba39d57f50c5188a8e32b9dd4f52d01611fe` (2026-07-17). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync --locked --group dev` — `pyproject.toml` / `uv.lock`; run from the repository root.

### Build
- `uv build` — `pyproject.toml`; run from the repository root.

### Dev
- `uv run ucc` — `pyproject.toml` (the `ucc` project script entry point); run from the repository root.

### Test
- Not detected

### Lint
- `uv run --group dev ruff check src/` — `Taskfile.yml`; run from the repository root.

### Type Check
- `uv run --group dev pyrefly check src/` — `Taskfile.yml`; run from the repository root.

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

Unoplat Code Confluence CLI deploys and operates a local Code Confluence Docker Compose stack from pinned GitHub release manifests for the Flow Bridge, query engine, and frontend. It validates repository remotes and provider credentials, adds and refreshes repositories, and triggers model-assisted AGENTS.md updates that result in pull requests.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

## Architecture
See [`architecture.md`](./architecture.md) for the canonical system architecture diagram.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
