<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `3bbc2c8ae5f6fc7e94628c3b07a936ca5bdbcd02` (2026-06-09). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync` — run from the repository root using `pyproject.toml`.

### Build
- `uv build --package unoplat-code-confluence-openmetadata` — run from the repository root using `pyproject.toml`.

### Dev
- Not detected.

### Test
- `uv run pytest` — run from the repository root using `pyproject.toml`.

### Lint
- `uv run ruff check src tests` — run from the repository root using `pyproject.toml`.

### Type Check
- `uv run basedpyright` — run from the repository root using `pyproject.toml`.

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description
This project is an OpenMetadata ingestion connector for Code Confluence, a repository-analysis system that turns query-engine snapshots into catalog assets. It publishes a developer-tooling domain and data product, then maps each codebase into API services, collections, and route-level endpoints enriched with engineering workflow, dependency, business-logic, and interface metadata. The core business focus is capturing deterministic source-code context and evidence so developers and AI agents can navigate repository behavior inside OpenMetadata.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
