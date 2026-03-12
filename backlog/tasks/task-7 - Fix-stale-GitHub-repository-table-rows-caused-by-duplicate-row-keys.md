---
id: TASK-7
title: Fix stale GitHub repository table rows caused by duplicate row keys
status: Done
assignee: []
created_date: '2026-03-03 12:11'
updated_date: '2026-03-10 09:31'
labels:
  - frontend
  - bugfix
  - data-table
dependencies: []
references:
  - >-
    unoplat-code-confluence-frontend/src/components/custom/RepositoryDataTable.tsx
priority: high
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate and resolve corrupted/stale search results in the GitHub Repositories table on `/onboarding/github`. Root cause identified as non-unique React row keys (`getRowId: row.name`) causing reconciliation collisions when repository names repeat (for example `fastapi`). Updated table row identity to use stable unique key `row.git_url`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 GitHub repository table uses a globally unique row identifier
- [x] #2 Typing and clearing search no longer leaves duplicated/corrupted rows
- [x] #3 No duplicate React key warnings are emitted for repository rows
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Resolved stale/corrupted GitHub repository table results by fixing row identity in `unoplat-code-confluence-frontend/src/components/custom/RepositoryDataTable.tsx`. Updated `getRowId` from `row.name` to `row.git_url` to guarantee globally unique keys and prevent React reconciliation collisions when multiple repositories share the same name (e.g. `fastapi`). Verified behavior manually: searching and clearing no longer leaves mixed/duplicated rows.
<!-- SECTION:FINAL_SUMMARY:END -->
