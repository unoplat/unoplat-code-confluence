---
id: TASK-14
title: Proactively disable already-ingested repos in onboarding picker
status: To Do
assignee: []
created_date: '2026-03-13 11:12'
labels:
  - frontend
  - ux
  - repository-operations
dependencies:
  - TASK-13
references:
  - >-
    unoplat-code-confluence-frontend/src/components/custom/RepositoryDataTable.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/repository-data-table-columns.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/IngestedRepositoriesDataTable.tsx
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from Task 13 (duplicate prevention). Task 13 handles the backend 409 guard and frontend error-based redirect. This task adds the proactive UX layer:

1. Fetch ingested repositories in `RepositoryDataTable` using `useQuery(["ingestedRepositories"], getIngestedRepositories)` — same query/cache as Repository Operations
2. Build a `Set<string>` of `"owner/name"` keys for O(1) per-row lookup
3. Pass the Set to `getRepositoryDataTableColumns` and render "Already Ingested" (disabled) instead of "Ingest Repo" for matching rows
4. Invalidate the `["ingestedRepositories"]` query on successful first-time ingest so the row updates immediately

This improves the UX by preventing users from even attempting to submit already-ingested repos, rather than relying solely on the backend 409 rejection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Onboarding picker shows 'Already Ingested' (disabled) for repos that exist in the ingested repositories list
- [ ] #2 The ingested repos lookup Set refreshes after a successful first-time ingest
- [ ] #3 Both GITHUB_OPEN and GITHUB_ENTERPRISE provider flows covered
<!-- AC:END -->
