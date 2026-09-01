<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `a5948971aedbc9c28b0f70964454c7f6a7c4d6da` (2026-08-31). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync` (working directory: repository root; config: `pyproject.toml`, `uv.lock`, `Taskfile.yml`)
### Build
- `uv build` (working directory: repository root; config: `pyproject.toml`)
### Dev
- Not detected
### Test
- `uv run pytest -v tests/` (working directory: repository root; config: `pyproject.toml`, `Taskfile.yml`)
### Lint
- `uvx ruff check .` (working directory: repository root; config: `ruff.toml`)
### Type Check
- `uv run --group dev pyrefly check src/` (working directory: repository root; config: `pyproject.toml`, `Taskfile.yml`)

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This package supports Code Confluence, a repository ingestion and code-intelligence platform. Its models track Git repositories, codebases, workflow runs, credentials, and agent progress while storing structural signatures, framework features, and detected source-code spans across Python and TypeScript. It also carries metadata for AGENTS.md publication and repository-level status/event tracking.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
