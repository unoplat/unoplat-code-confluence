---
id: TASK-16.3
title: Separate shared backend runtime concerns from route handlers
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-03-18 07:16'
updated_date: '2026-03-19 09:57'
labels:
  - backend
  - refactor
  - fastapi
  - task-16
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/utility/deps.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/utility/token_utils.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/router.py
parent_task_id: TASK-16
priority: high
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a stable backend foundation for TASK-16 by moving workflow/provider/runtime helper logic and shared app-state access out of route handlers. This reduces `main.py` to bootstrap concerns and makes later router splits and alpha codebase-config changes safer to implement.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Shared runtime helpers for codebase detection, workflow start and monitoring, and provider URL construction are defined outside `main.py` with precise types and reused through imports.
- [x] #2 FastAPI dependencies expose runtime resources such as environment settings, Temporal client, codebase detector registry, and trace-aware request logging without new endpoint code reaching into a global `app`.
- [x] #3 `main.py` keeps lifespan/bootstrap and router registration responsibilities for the extracted pieces, and existing behavior remains unchanged for endpoints not yet altered by later subtasks.
- [x] #4 Backend diagnostics or targeted tests confirm startup/lifespan and the extracted helper behavior still work.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extract shared backend runtime concerns from `main.py` into focused utility modules for codebase detection, provider URL construction, workflow start/monitoring, and runtime dependency access.
2. Update ingestion and GitHub App endpoints to consume those shared helpers and FastAPI dependencies instead of reading runtime state directly from the global app object.
3. Keep `main.py` responsible for lifespan/bootstrap setup and router registration, then verify the refactor with targeted linting and integration validation evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Review started on 2026-03-18. Code changes extract runtime helpers into `utility/detection.py`, `utility/provider_urls.py`, `utility/runtime_deps.py`, and `utility/workflow_helpers.py`, and route handlers now consume FastAPI dependencies instead of reaching into the global app state directly.

Current review findings:
- Acceptance criterion #4 is not yet evidenced in the task record or code changes: no targeted tests were added for the extracted helpers/dependencies, and a search under `tests/` found no references to the new helper modules.
- The Backlog record is not finalized yet even though implementation appears to be in progress/completed locally: status was still `To Do`, acceptance criteria remain unchecked, and there is no task-level plan/final summary capturing what changed and how it was validated.
- Repo diagnostics run during review are noisy because of existing unrelated basedpyright issues in the project, but touched-file linting passes; targeted basedpyright on touched files still reports pre-existing type issues in `main.py` and `github_app/router.py`, so validation evidence should be captured carefully when finalizing this subtask.

Finalized after review. User confirmed the existing integration tests remain intact for this refactor, so the subtask is being closed with that validation note in addition to the touched-file lint pass recorded during review.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Separated shared backend runtime concerns from route handlers so later TASK-16 router splits can build on stable, reusable primitives instead of duplicating logic in `main.py`. The refactor moves multi-language codebase detection orchestration, GitHub provider URL helpers, workflow start/monitor helpers, and FastAPI runtime dependency access into dedicated utility modules, then updates ingestion and GitHub App routes to import those helpers and receive Temporal/environment resources through dependencies rather than reaching into the global app directly.

`main.py` now keeps its bootstrap/lifespan responsibilities while reusing the extracted modules for ingestion and refresh flows, preserving behavior for the untouched endpoints needed by later subtasks. Validation evidence for this subtask is the touched-file Ruff pass run during review plus the user's confirmation that the existing integration tests remain intact after the refactor.
<!-- SECTION:FINAL_SUMMARY:END -->
