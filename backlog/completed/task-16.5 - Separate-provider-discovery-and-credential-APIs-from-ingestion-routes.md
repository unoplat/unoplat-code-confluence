---
id: TASK-16.5
title: Separate provider discovery and credential APIs from ingestion routes
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-03-18 07:17'
updated_date: '2026-03-18 13:47'
labels:
  - backend
  - refactor
  - credentials
  - task-16
dependencies:
  - TASK-16.3
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/utility/token_utils.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py
parent_task_id: TASK-16
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Isolate provider discovery and credential management from repository ingestion so onboarding and provider lookup can evolve independently of TASK-16 ingestion changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Dedicated router modules own token CRUD, flags, repository provider listing, repository discovery, and authenticated user details endpoints.
- [x] #2 Provider-specific GraphQL and REST lookup logic is extracted into reusable service or helper code rather than embedded in route handlers.
- [x] #3 Existing response shapes and operator behavior remain intact after the split.
- [x] #4 Relevant backend tests cover the moved endpoints and touched typecheck/lint checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create three dedicated router modules under `src/code_confluence_flow_bridge/routers/` so `main.py` stops owning these handlers directly while exact HTTP paths stay unchanged:
   - `credentials/router.py` for `POST /ingest-token`, `PUT /update-token`, and `DELETE /delete-token`
   - `providers/router.py` for `GET /repository-providers`, `GET /repos`, and `GET /user-details`
   - `flags/router.py` for `GET /flags`, `GET /flags/{flag_name}`, and `PUT /flags/{flag_name}`
2. Add focused shared helper/service code instead of moving inline logic verbatim:
   - credential mutation helpers for create/update/delete flows, bearer token extraction, and `isTokenSubmitted` flag synchronization
   - provider lookup helpers for configured-provider listing, GitHub GraphQL repository discovery, filter parsing, and authenticated-user REST lookups
   - keep reusing shared runtime utilities from `TASK-16.3` (`fetch_repository_provider_token`, provider URL helpers) rather than duplicating provider wiring in routers
3. Preserve all existing contracts while extracting:
   - keep current response models from `src/code_confluence_flow_bridge/models/github/github_repo.py`
   - keep current query/header parameter names (`authorization`, `namespace`, `provider_key`, `secret_kind`, `url`, `filterValues`, `cursor`, `per_page`)
   - preserve current error semantics where already intentional, especially 401/404/409 cases for credential flows and upstream status passthrough for `/user-details`
4. Update `src/code_confluence_flow_bridge/main.py` to register the new routers and remove the moved handlers/imports, following the router registration pattern already established by `TASK-16.4`.
5. Add or extend backend coverage for the moved endpoints with emphasis on the refactor boundaries:
   - credential CRUD + `isTokenSubmitted` flag behavior
   - configured repository provider listing
   - repository discovery `/repos` success path and filter parsing failure path
   - authenticated user details lookup including fallback email fetch behavior
   - touched flags endpoints if coverage is currently missing
6. Verification order after implementation:
   - `uv run --group dev basedpyright src/`
   - `uv run ruff check src/`
   - `uv run ruff format src/`
   - targeted `uv run --group test pytest ... -v` for the touched integration tests covering credentials/provider routes
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Marked complete based on user confirmation that the credentials/providers/flags refactor is finished. Acceptance criteria were checked and the task status was advanced to Done per the requested milestone update.

Added schema-driven tree-sitter regression tests for FastAPI router-decorated endpoints (`from fastapi import APIRouter` and `from fastapi.routing import APIRouter`) before changing the FastAPI framework definition. Updated `framework-definitions/python/fastapi.json` so `http_endpoint` includes APIRouter-based route decorators and `api_router` also recognizes `fastapi.routing.APIRouter` for include-router style detection.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Separated provider discovery, credential management, and flag endpoints from ingestion concerns by moving them into dedicated router modules with shared helper logic for token mutation, provider lookups, and authenticated user discovery. This keeps `main.py` focused on application composition while preserving existing request/response contracts and operator-facing behavior for token CRUD, provider listing, repository discovery, flags, and user details.

This subtask completes the backend route/service split required before implementing the alpha TASK-16 detection-preview and saved-config ingestion contract. Marked Done based on user confirmation that implementation and verification for this refactor are complete.
<!-- SECTION:FINAL_SUMMARY:END -->
