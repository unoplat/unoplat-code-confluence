## Engineering Workflow
- Install: `task install` (config: `Taskfile.yml`).
- Test: `task test` (config: `Taskfile.yml`).

## Dependency Guide
- **Overview**: Full dependency descriptions are maintained in `dependencies_overview.md`.
- **Usage**: Keep this section concise and treat `dependencies_overview.md` as the source-of-truth dependency catalog.

## Business Logic Domain
- **Domain overview:** This codebase models a “code confluence” platform that ingests git repositories and codebases, stores structural signatures of source files, and detects framework-specific features using configurable queries and metadata. It also tracks workflow runs for repository and codebase processing, including statuses, errors, events, and agent output snapshots, alongside package manager and language metadata. Supporting models handle credentials, feature flags, and PR publication metadata for automated documentation or agent output updates.
- **Core model groups:**
  - Structural signatures and positioning primitives: `python_structural_signature.py`, `typescript_structural_signature.py`, `data_model_position.py`.
  - Framework feature definitions, imports, and query matching: `framework_models.py`.
  - Repository/codebase persistence, file inventories, and relational mappings: `relational_models/unoplat_code_confluence.py`, `repo_models.py`, `engine_models.py`.
  - Workflow execution tracking (runs, statuses, errors, snapshots): `workflow_models.py`, `workflow_envelopes.py`.
  - Configuration and operational metadata (credentials, flags, metadata, PR publication): `configuration_models.py`, `credentials.py`, `flags.py`, `programming_language_metadata.py`, `pr_metadata_model.py`.
- **References:** See `business_logic_references.md` for a file-by-file map of business logic models.

## App Interfaces
- **Overview:** No app interface constructs have been documented for this codebase yet.
- **Inbound interfaces:** None documented.
- **Outbound interfaces:** None documented.
- **Internal interfaces:** None documented.
- **References:** See `app_interfaces.md` for the tracked interface inventory.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `a6db7131de30314e9053e74a395ac31be9cb767a` (2026-04-25). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync` (config: `pyproject.toml`, `Taskfile.yml`)
### Build
- `uv build` (config: `pyproject.toml`)
### Dev
- Not detected
### Test
- `uv run pytest -v tests/` (config: `pyproject.toml`, `Taskfile.yml`)
### Lint
- Not detected
### Type Check
- Not detected

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
