<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `d9ab7533d1fedb930cd2344898a111e091ac4d8b` (2026-06-19). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync --group dev --group test` — run from the repository root using `pyproject.toml`; matches `Taskfile.yml` task `sync`.

### Build
- `uv build --package unoplat-code-confluence-openmetadata` — run from the repository root using `pyproject.toml`.

### Dev
- Not detected.

### Test
- `uv run --group test pytest -v tests/` — run from the repository root using `pyproject.toml`; matches `Taskfile.yml` task `test`.

### Lint
- `uv run --group dev ruff check src/` — run from the repository root using `pyproject.toml`; matches `Taskfile.yml` task `lint`.

### Type Check
- `uv run --group dev pyrefly check src/` — run from the repository root using `pyproject.toml`; matches `Taskfile.yml` task `typecheck`.

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This project is an OpenMetadata ingestion connector for Code Confluence, a repository-analysis system that turns query-engine snapshots into catalog metadata. It models each repository and codebase with programming language, engineering workflow, dependency, business-logic, and interface details so the results can be published and searched in OpenMetadata. The core business focus is capturing deterministic source-code context and evidence for repository understanding and discovery.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
