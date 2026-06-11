<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `3bbc2c8ae5f6fc7e94628c3b07a936ca5bdbcd02` (2026-06-09). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync --locked --group dev` — `pyproject.toml` / `uv.lock`

### Build
- `uv build` — `pyproject.toml`

### Dev
- `uv run unoplat` — `pyproject.toml` (project script entry point)

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
Unoplat Code Confluence CLI manages the local Code Confluence Docker Compose stack: it fetches and pins GitHub releases, installs or repairs release assets, starts the Flow Bridge/query engine/frontend services, and opens browser setup pages for repository token and model-provider configuration.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
