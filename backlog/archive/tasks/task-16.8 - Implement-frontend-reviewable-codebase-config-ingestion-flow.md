---
id: TASK-16.8
title: Implement frontend reviewable codebase-config ingestion flow
status: To Do
assignee: []
created_date: '2026-03-18 07:20'
labels:
  - frontend
  - ingestion
  - repository-operations
  - alpha
  - task-16
dependencies:
  - TASK-16.6
  - TASK-16.7
references:
  - >-
    unoplat-code-confluence-frontend/src/components/custom/RepositoryDataTable.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/IngestedRepositoriesDataTable.tsx
  - unoplat-code-confluence-frontend/src/lib/api.ts
  - unoplat-code-confluence-frontend/src/types.ts
parent_task_id: TASK-16
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the Paper-designed frontend flow so users can preview detected codebases, review/customize the approved subset, view saved config, and explicitly re-detect when managing an ingested repository.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Onboarding `Ingest Repo` opens the detection preview dialog with `Ingest All (n)` as the fast path and `Review & Customize` as the secondary flow.
- [ ] #2 The review and customize UI supports selection-first editing with inline expanded rows limited to `codebase_folder`, `project_name`, `language`, and `package_manager`.
- [ ] #3 Repository operations expose saved config viewing and explicit re-detect confirmation and review flows aligned with the Paper screens.
- [ ] #4 Frontend tests cover the new flow and touched typecheck/lint checks pass.
<!-- AC:END -->
