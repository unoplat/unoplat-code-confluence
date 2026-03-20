---
id: TASK-16
title: Add reviewable codebase detection for ingestion and monorepos
status: To Do
assignee:
  - OpenCode
created_date: '2026-03-18 06:58'
updated_date: '2026-03-19 09:57'
labels:
  - ingestion
  - frontend
  - backend
  - typescript
  - repository-operations
  - alpha
dependencies: []
references:
  - >-
    unoplat-code-confluence-frontend/src/components/custom/RepositoryDataTable.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/IngestedRepositoriesDataTable.tsx
  - unoplat-code-confluence-frontend/src/lib/api.ts
  - unoplat-code-confluence-frontend/src/types.ts
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/typescript_ripgrep_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/repository_metadata_service.py
priority: high
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ship the alpha codebase-configuration flow from Paper so repository ingestion always starts with detected codebases, keeps `Ingest All` as the fast path, offers optional review/customization before submission, and makes the approved saved config the source of truth for repository operations. This also includes hardening TypeScript workspace detection so aggregator and leaf packages are identified correctly for the new UI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Initial ingestion remains a fast default flow in alpha: clicking `Ingest Repo` shows detected codebases and supports a primary `Ingest All (n)` action without requiring manual review.
- [ ] #2 The backend exposes a pre-ingestion codebase-detection preview that returns detected `CodebaseConfig` entries without starting workflows, and ingestion submits the approved subset through explicit `repository_metadata` as the primary alpha contract.
- [ ] #3 The ingest UI offers a secondary review flow where users can deselect detected codebases and make lightweight edits to the fields shown in design before submission.
- [ ] #4 After first approval, saved repository codebase config is used by default for refresh or re-ingestion, and Repository Operations provides explicit actions to view saved config and replace it through a fresh re-detect flow.
- [ ] #5 TypeScript workspace-based repositories detect nested workspace packages without a detected root suppressing them, and detected TypeScript codebases populate identity fields needed by the new UI, including project name, package manager, and role metadata.
- [ ] #6 Regression coverage confirms the designed alpha flow works end to end: detection preview, `Ingest All`, reviewed subset ingestion, TypeScript monorepo detection, saved-config reuse, explicit re-detect replacement, and existing saved-config consumers continue to work.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementation plan (alpha-only rollout)

Design source reviewed on Paper page `codebase-configuration-flow` with 7 product screens plus the onboarding baseline artboard. This work should follow the designed alpha flow directly.

1. Backend detection and config APIs
- Add a `POST /detect-codebases` preview endpoint that returns detected `CodebaseConfig[]` without starting workflows or persisting repository state so Screen 2 can render immediately after the onboarding row action.
- Update `POST /start-ingestion` so explicit approved `repository_metadata` from the preview/review flow is the primary alpha contract.
- Add or adapt repository-operations endpoints so saved codebase config can be read for the view dialog and replaced through an explicit re-detect flow.
- Refactor refresh/re-ingestion semantics so saved approved config is the default source of truth, and only the explicit re-detect path replaces it.

2. Onboarding flow implementation by screen
- Screen 1: keep the onboarding repositories table as the entry point and wire the row action `Ingest Repo` to call detection preview first instead of immediately calling ingestion.
- Screen 2: build a compact detection preview dialog titled `Detected Codebases` that lists each detected codebase as folder + metadata badges + project name, with primary action `Ingest All (n)` and secondary action `Review & Customize`.
- Screen 3: build the review dialog with checkbox selection per codebase, preserve badge metadata in collapsed rows, and drive the CTA label from the selected count (`Ingest Selected (n)`).
- Screen 4: support one expanded row at a time with lightweight inline editing limited to the fields shown in design: `codebase_folder`, `project_name`, `language`, and `package_manager`. Do not expose `root_packages` in the UI.
- For the editable folder field, implement assisted selection/autocomplete from detected candidate folders rather than arbitrary codebase authoring from scratch, matching the design intent.

3. Repository Operations implementation by screen
- Screen 5: extend the repository row actions to support the new codebase-config management flow while preserving existing operations actions and status presentation.
- Screen 6: add a read-focused `Codebase Configuration` dialog for saved config that shows the saved badge plus rows with folder, language, package manager, role badge (`leaf`/`aggregator`), and project name.
- Screen 7: add the `Re-detect Codebases?` confirmation flow and route it into the same reviewable detection-preview path before any saved config is replaced.
- Because the Paper set includes a re-detect confirmation screen but does not visibly show the launch affordance in the row-menu/config-dialog artboards, implement the trigger in the most local repository-operations entry point already used for config management and keep it isolated so the affordance can be repositioned later without API changes.

4. Data model and metadata alignment
- Treat the visible editable/viewable fields from Paper as the frontend contract: `codebase_folder`, `project_name`, `language`, `package_manager`, and role/status badges where available.
- Remove `root_packages` from the designed UX and avoid making it part of the new alpha contract.
- Simplify stored and detected metadata around folder, manifest, project name, package-manager metadata, and role information instead of keeping `root_packages` as a first-class concept for this feature.
- Ensure role metadata (`leaf` vs `aggregator`) is populated by TypeScript detection so the badges shown in Screens 2, 3, 4, and 6 can be rendered from real backend data.

5. TypeScript monorepo detection hardening
- Update TypeScript detection to recognize workspace aggregator roots and nested workspace leaves so the detector returns entries like the design example (`apps/web`, `packages/core`, `packages/ui`) instead of collapsing to repository root.
- Do not let an aggregator root suppress nested leaf packages.
- Populate `project_name`, `manifest_path`, package-manager metadata, and role information from workspace/package manifests wherever possible.
- Do not rely on `root_packages` for TypeScript identity or UI flows.

6. Validation and regression coverage
- Add backend tests for detection preview, explicit approved ingestion payloads, saved-config default reuse, and explicit re-detect replacement.
- Add detector coverage for TypeScript workspace repos that verifies aggregator + leaf outputs and protects against root suppression of nested packages.
- Add frontend coverage for the full Paper flow: onboarding action -> detection preview -> review/customize -> inline edit -> ingest selected; plus repository operations view-config and re-detect confirmation.
- Run touched frontend/backend type checks, linting, and relevant tests after implementation.

Approved subtask breakdown and sequencing (2026-03-18)

1. `TASK-16.3` — Separate shared backend runtime concerns from route handlers. Establish extracted helpers and FastAPI dependencies so later router work does not depend on the global app object.
2. `TASK-16.4` — Separate repository config and status APIs from app bootstrap. Move saved-config/status/admin reads into dedicated routers/services.
3. `TASK-16.5` — Separate provider discovery and credential APIs from ingestion routes. Move token/provider/user lookup endpoints and shared GitHub provider logic.
4. `TASK-16.6` — Deliver alpha backend detection preview and saved-config ingestion flow. Add the detection-preview contract, explicit approved `repository_metadata` handling, and saved-config/re-detect semantics.
5. `TASK-16.7` — Improve TypeScript workspace detection for alpha codebase config. Harden workspace aggregator/leaf detection and metadata population for the alpha UI.
6. `TASK-16.8` — Implement frontend reviewable codebase-config ingestion flow. Build the Paper-aligned onboarding and repository-operations UI on top of the backend contract.
7. `TASK-16.1` — Validate the end-to-end TASK-16 alpha flow. Run the final integration-oriented validation pass and capture accepted alpha limitations.

Dependency summary
- `TASK-16.4` depends on `TASK-16.3`
- `TASK-16.5` depends on `TASK-16.3`
- `TASK-16.6` depends on `TASK-16.3`, `TASK-16.4`, and `TASK-16.5`
- `TASK-16.8` depends on `TASK-16.6` and `TASK-16.7`
- `TASK-16.1` depends on `TASK-16.8`, `TASK-16.6`, and `TASK-16.7`

Implementation note: `TASK-16.2` was archived after task creation because it duplicated the frontend subtask during a tool race; `TASK-16.8` is the active frontend implementation task.

Correction (2026-03-18): the active frontend implementation subtask is `TASK-16.2`. `TASK-16.8` was archived as the duplicate created during the task-creation race, so downstream work should target `TASK-16.2` and the final validation dependency chain should read `TASK-16.1` depends on `TASK-16.2`, `TASK-16.6`, and `TASK-16.7`.

Progress update (2026-03-18): `TASK-16.3`, `TASK-16.4`, and `TASK-16.5` are complete. Remaining sequence is `TASK-16.6` -> `TASK-16.7` -> `TASK-16.2` -> `TASK-16.1`.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Codebase and design review notes

- `unoplat-code-confluence-frontend/src/components/custom/RepositoryDataTable.tsx:34` always submits `repository_metadata: null`, so the current frontend cannot exercise curated codebase selection even though the request type already supports it.
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py:1075` already accepts explicit `repository_metadata`, which makes it a good fit for the new alpha contract.
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py:1667` refreshes by re-detecting codebases on every run today, which conflicts with the desired `saved curated config is canonical until explicitly changed` behavior.
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py:72` already persists and updates codebase configs from the workflow envelope, so approved metadata can be stored without inventing a new persistence path.
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py:1427` and `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/repository_metadata_service.py:24` show downstream consumers already rely on saved codebase config, so changes must preserve that contract.
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/typescript_ripgrep_detector.py:156` uses `done_dirs` to suppress nested directories once a parent is detected, and the detector schema already has `workspace_field` support even though the TypeScript rules and detector flow do not currently use it.
- Paper design review on page `codebase-configuration-flow` found 8 artboards: the onboarding baseline plus Screens 1-7 for the new flow.
- Screen 2 (`Detected Codebases`) shows the fast path clearly: list detected codebases with badges and project names, primary CTA `Ingest All (n)`, secondary CTA `Review & Customize`.
- Screen 3 (`Review Codebases`) confirms review is selection-first, with checkbox deselection and a count-driven submit CTA. Aggregator rows can be deselected just like leaf rows.
- Screen 4 (`Inline Edit Expanded Row`) limits editing to `Codebase Folder`, `Project Name`, `Language`, and `Package Manager`, with folder suggestions/autocomplete visible. The design does not expose `root_packages`, so the new UI should not depend on it.
- Screen 5 (`Repository Operations`) keeps repository actions in a row menu and adds config management to the operations area; the visible menu item is `View Codebase Config`.
- Screen 6 (`Codebase Configuration`) is a read-oriented saved-config dialog showing a `Saved` badge plus folder, language badge, package manager badge, role badge, and project name for each codebase.
- Screen 7 (`Re-detect Codebases?`) makes the replacement semantics explicit: re-detect replaces saved config, but the user can review detected codebases before replacement. This should drive the backend contract for explicit re-detect.
- Design gap noted during review: Screen 7 exists but its launch affordance is not visible in the repository-operations artboards. Implementation should keep the re-detect trigger modular so it can be repositioned later without changing the underlying API flow.
- Product direction updated: this feature is shipping in alpha, so backward compatibility is not required for legacy null-metadata ingestion paths.
- `root_packages` should be treated as out of scope for the new UX and no longer drives the feature design; the alpha contract should center on folder, project name, language, package manager, manifest-derived metadata, and role.

Started planning a focused backend refactor for `code_confluence_flow_bridge.main` to split endpoints into SRP-aligned routers as part of TASK-16. Reviewing existing route groupings, shared dependencies, and FastAPI router patterns before proposing the implementation breakdown.

Split TASK-16 into execution subtasks covering backend foundations, router separation, alpha backend contracts, TypeScript detector hardening, frontend flow implementation, and final integration validation.

Corrected the frontend subtask reference after backlog task creation stabilized: `TASK-16.2` is the active frontend task and `TASK-16.8` was archived as a duplicate.

Status update: subtasks `TASK-16.3`, `TASK-16.4`, and `TASK-16.5` are now marked Done. The backend foundation and route extraction work up through provider/credential separation is complete, so the next implementation target in sequence is `TASK-16.6`.
<!-- SECTION:NOTES:END -->
