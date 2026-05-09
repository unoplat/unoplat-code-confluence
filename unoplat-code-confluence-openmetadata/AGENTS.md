<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `e1d9b8966ae6d91f530e642d0fb01662c3cf2760` (2026-05-09). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync --all-groups` — repo root (`pyproject.toml`)

### Build
- `uv build --package unoplat-code-confluence-openmetadata` — repo root (`pyproject.toml`)

### Dev
- `docker compose -f docker-compose.yml up --detach` — `deployment/` (`deployment/docker-compose.yml`)

### Test
- `uv run --group test pytest` — repo root (`pyproject.toml`)

### Lint
- `uv run ruff check src` — repo root (`pyproject.toml`)

### Type Check
- `uv run basedpyright` — repo root (`pyproject.toml`)

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

The project is a developer-tooling OpenMetadata connector for Code Confluence. It ingests repository snapshots from a query-engine and maps them into catalog assets such as API services, codebase collections, endpoints, domains, data products, glossary terms, and evidence-backed business-logic metadata.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
