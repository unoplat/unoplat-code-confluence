---
id: TASK-17
title: Deliver alpha backend detection preview and saved-config ingestion flow
status: To Do
assignee: []
created_date: '2026-03-19 05:02'
updated_date: '2026-03-19 09:57'
labels:
  - backend
  - ingestion
  - repository-config
  - alpha
dependencies:
  - TASK-16.3
  - TASK-16.4
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py
priority: high
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deliver the alpha backend contract so first-time repository ingestion starts from a reviewable detection preview, while later refresh or re-ingestion reuses the saved approved codebase config by default, validates it against the current repository structure, and only asks users to review fresh detections when the saved config is no longer valid or they explicitly re-detect.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Backend exposes a detection-preview endpoint for first-time ingestion and explicit re-detect flows that returns detected `CodebaseConfig` entries without starting workflows or persisting repository state.
- [ ] #2 Initial ingestion accepts explicit approved `repository_metadata` as the primary alpha contract and no longer depends on legacy null-metadata auto-detection for the new flow.
- [ ] #3 Repository refresh and re-ingestion default to saved approved config, skip re-detection on the happy path, validate that saved codebase folders still exist before starting workflows, and fail with an actionable update-codebases response when saved config is stale instead of silently replacing it.
- [ ] #4 Explicit re-detect flows return fresh detections for review before replacement, and backend tests cover detection preview, approved-subset ingestion, saved-config reuse, stale-folder validation failure with fresh detections, and explicit re-detect replacement.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Current code and design findings

- `unoplat-code-confluence-frontend/src/components/custom/RepositoryDataTable.tsx:34` still submits `repository_metadata: null`, so the current onboarding UI cannot exercise curated codebase selection yet.
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py:452` still auto-detects inside `/start-ingestion` when `repository_metadata` is null or empty. That behavior no longer matches the alpha flow.
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/repository/router.py:363` currently re-detects codebases on every refresh. This conflicts with the product direction that saved approved config is canonical until explicitly changed.
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py:72` already persists approved codebase config from the workflow envelope, so this task can reuse the existing persistence path instead of inventing a new store.
- That same persistence path only inserts or updates `CodebaseConfig` rows today; it does not remove stale rows. Reviewed replacement flows therefore need explicit deletion of no-longer-approved codebases before or during persistence.
- Saved-config consumers already exist and must keep working: `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/repository/router.py:209` exposes saved config, and `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/repository_metadata_service.py:24` consumes saved config downstream.
- `root_packages` is not part of the designed alpha UX. Backend request and response handling for this task should center on `codebase_folder`, `project_name`, `language`, `package_manager`, `manifest_path`, and role-oriented metadata where available.
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/repository/mappers.py:21` currently maps only language/package manager/version/manifest/project name from saved metadata, so this task should avoid hard-coding a contract that blocks the role metadata needed by TASK-16.7.

Paper flow takeaways

- Screen 2 (`Detected Codebases`) establishes a side-effect-free preview step with a fast path `Ingest All (n)` and a secondary `Review & Customize` path.
- Screen 3 (`Review Codebases`) confirms review is selection-first. Users can deselect both leaf and aggregator entries before submission.
- Screen 4 limits inline edits to `Codebase Folder`, `Project Name`, `Language`, and `Package Manager`, with assisted folder selection rather than arbitrary authoring.
- Screen 6 (`Saved Codebase Configuration`) is read-oriented and shows the persisted saved config as the source of truth for repository operations.
- Screen 7 (`Validation Failure / Update Codebases`) makes the update path explicit: refresh validates saved config first, and only broken saved config routes users into a reviewed replacement flow.

Critique outcome and backend direction

- I agree with the requested product change: first-time ingestion should stay detection-first and reviewable, but routine refresh/update should not force users through re-detection when folder structure is stable.
- Recommended backend split:
  - first ingestion or explicit re-detect -> run detection preview, let the user approve or edit the set, then ingest with explicit approved `repository_metadata`
  - refresh/update of an already ingested repository -> skip preview and full re-detection on the happy path, load saved approved config, validate that each saved `codebase_folder` still exists in the current repository snapshot, and start ingestion directly if validation passes
- Do not silently fall back from failed validation into auto-detect plus ingestion. Silent replacement would make refresh behavior nondeterministic and would mutate the approved contract without user review.
- When saved-config validation fails, fail before starting the workflow and return an actionable response that includes the invalid or missing saved folders plus a fresh detected candidate set so the frontend can send the user into an `Update Codebases` review flow.
- Validation failure during refresh should not overwrite saved config automatically. Explicit reviewed re-detect remains the only path that can replace persisted config.
- Recommended stale-config response shape should be easy for the frontend to branch on and include fields equivalent to: failure reason, invalid folder list, saved approved config, fresh detected config, and an explicit flag that review/update is required.
- Keep happy-path validation lightweight: verify saved `codebase_folder` presence first, and also verify `manifest_path` when present, so stable repositories bypass re-detection quickly while structural drift produces a precise failure.
- Because `main.py` now only owns `/start-ingestion` after TASK-16.3/16.4/16.5, this task is a good place to extract ingestion-specific routes into a dedicated router/service pair so detection preview, create ingestion, refresh validation, and reviewed replacement semantics live together.

Required regression coverage

- Detection preview creates no repository row and starts no workflow.
- First ingestion persists only the approved subset supplied through explicit `repository_metadata`.
- Refresh/update with stable saved folders skips re-detection and starts ingestion directly from saved config.
- Refresh/update with missing saved folders fails before workflow start and returns fresh detections for review.
- Explicit reviewed re-detect replacement removes stale saved rows and persists the replacement set.

Extracted from TASK-16.6 so TASK-16 can complete independently while this alpha backend flow stays in the backlog as a standalone follow-up.
<!-- SECTION:NOTES:END -->
