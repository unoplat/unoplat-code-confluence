<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `57d1d23304bfc4e45c00dae712eec11747f33c0d` (2026-07-24). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync --group dev --group test` — run from the repository root using `Taskfile.yml`.

### Build
- `uv build` — run from the repository root using `pyproject.toml`.

### Dev
- Not detected.

### Test
- `uv run --group test pytest -v tests/` — run from the repository root using `Taskfile.yml`.

### Lint
- `uv run --group dev ruff check src/` — run from the repository root using `Taskfile.yml`.

### Type Check
- `uv run --group dev pyrefly check src/` — run from the repository root using `Taskfile.yml`.

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This project is an OpenMetadata ingestion connector for Code Confluence, a repository-analysis system that turns query-engine snapshots into catalog assets. It publishes a developer-tooling domain and data product, then maps each codebase into API services, collections, and route-level endpoints enriched with engineering workflow, dependency, business-logic, and interface metadata. The core business focus is capturing deterministic source-code context and evidence so developers and AI agents can navigate repository behavior inside OpenMetadata.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

## Architecture
See [`architecture.md`](./architecture.md) for the canonical system architecture diagram.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
