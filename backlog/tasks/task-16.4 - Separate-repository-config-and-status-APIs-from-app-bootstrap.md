---
id: TASK-16.4
title: Separate repository config and status APIs from app bootstrap
status: Done
assignee:
  - OpenCode
created_date: '2026-03-18 07:17'
updated_date: '2026-03-19 09:57'
labels:
  - backend
  - refactor
  - repository-config
  - task-16
dependencies:
  - TASK-16.3
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/repository_metadata_service.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/app_interfaces.md
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_delete_repository.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_start_ingestion.py
parent_task_id: TASK-16
priority: high
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Give TASK-16 a clear backend home for saved repository configuration, repository lifecycle APIs, and global operations visibility by moving the relevant handlers out of `main.py` into dedicated routers and shared services. Repository-scoped endpoints should live under a repository router, while cross-repository operational listing endpoints should move into a separate operations router.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A dedicated repository router owns the repository-scoped endpoints currently defined in `main.py`: `/repository-status`, `/repository-data`, `/codebase-metadata`, `/delete-repository`, and `/refresh-repository`.
- [x] #2 A separate operations-oriented router owns the cross-repository listing endpoints currently defined in `main.py`: `/parent-workflow-jobs` and `/get/ingestedRepositories`.
- [x] #3 Existing response models, exact HTTP paths, dependency injection behavior, and current consumer behavior remain intact while these handlers are removed from `main.py`.
- [x] #4 Shared mapping logic for repository/config/status responses is extracted or reused instead of copied between handlers.
- [x] #5 Relevant backend tests cover the moved endpoints and touched typecheck/lint/format checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/repository/__init__.py`, `service.py`, and `router.py`.
2. In `service.py`, add shared top-level helpers:
   - `build_programming_language_metadata(raw_metadata: dict[str, Any]) -> ProgrammingLanguageMetadata`
   - `build_repository_status_hierarchy(codebase_runs: Sequence[CodebaseWorkflowRun]) -> Optional[CodebaseStatusList]`
3. Move the repository-scoped handlers from `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py` into `routers/repository/router.py` with `APIRouter(prefix="", tags=["Repository"])`:
   - `GET /repository-status`
   - `GET /repository-data`
   - `GET /codebase-metadata`
   - `DELETE /delete-repository`
   - `POST /refresh-repository`
4. Replace duplicated inline metadata mapping in `/repository-data` and `/codebase-metadata` with `build_programming_language_metadata`, and replace the inline repository status hierarchy builder in `/repository-status` with `build_repository_status_hierarchy`.
5. Create `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/operations/__init__.py` and `router.py`.
6. Move the cross-repository operations endpoints from `main.py` into `routers/operations/router.py` with `APIRouter(prefix="", tags=["Operations"])`:
   - `GET /parent-workflow-jobs`
   - `GET /get/ingestedRepositories`
7. Update `main.py` to import and register both routers, remove the moved handlers, and clean up imports that are no longer used there.
8. Preserve exact endpoint paths and signatures so existing consumers and integration tests continue to work unchanged.
9. Verification order:
   - `uv run --group dev basedpyright src/`
   - `uv run ruff check src/`
   - `uv run ruff format src/`
   - `uv run --group test pytest tests/integration/test_delete_repository.py -v`
   - `uv run --group test pytest tests/integration/test_start_ingestion.py -v`
10. Optional follow-up if the extraction introduces meaningful pure transformation logic worth isolating further: add unit tests for the repository service helpers in `tests/unit/routers/repository/test_service.py`.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated the task plan to split cross-repository operational listing endpoints (`/parent-workflow-jobs`, `/get/ingestedRepositories`) away from the repository router. Rationale: these endpoints operate on global workflow/repository inventory and are used by operations-facing flows rather than a single repository context.

Task status moved to In Progress. Awaiting implementation to review once the code changes are ready.

Marked complete based on user confirmation that the repository/config/status/admin router split is finished. Acceptance criteria were checked and the task status was advanced to Done per the requested milestone update.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Moved repository-scoped and operations-oriented APIs out of `main.py` into dedicated routers so TASK-16 now has a cleaner backend home for saved repository configuration, repository lifecycle operations, and global operational listings. The extraction preserves the existing HTTP paths and response behavior while centralizing shared mapping logic for repository status/config responses instead of duplicating it across handlers.

This subtask closes the repository/config/status router split needed before the alpha detection-preview work in later subtasks. Marked Done based on user confirmation that implementation and verification for this split are complete.
<!-- SECTION:FINAL_SUMMARY:END -->
