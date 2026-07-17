<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `5ecdba39d57f50c5188a8e32b9dd4f52d01611fe` (2026-07-17). Content may become stale as new commits land.

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

Unoplat Code Confluence CLI is a developer-tooling orchestration client for deploying and operating a local Code Confluence stack composed of Flow Bridge, Query Engine, and frontend services. It tracks GitHub release manifests and state to install, update, run, and tear down Docker Compose assets, while parsing repository remotes, checking repository/model-provider setup, and triggering refresh workflows that generate or update AGENTS.md through pull requests.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

## Architecture
See [`architecture.md`](./architecture.md) for the canonical system architecture diagram.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
