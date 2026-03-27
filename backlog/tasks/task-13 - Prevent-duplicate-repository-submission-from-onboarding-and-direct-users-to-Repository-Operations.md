---
id: TASK-13
title: >-
  Prevent duplicate repository submission from onboarding and direct users to
  Repository Operations
status: To Do
assignee: []
created_date: '2026-03-13 09:27'
updated_date: '2026-03-19 09:57'
labels:
  - frontend
  - backend
  - repository-operations
  - ux
dependencies: []
references:
  - >-
    unoplat-code-confluence-frontend/src/components/custom/RepositoryDataTable.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/repository-data-table-columns.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/IngestedRepositoriesDataTable.tsx
  - unoplat-code-confluence-frontend/src/routes/_app.repositoryOperations.tsx
  - unoplat-code-confluence-frontend/src/lib/api.ts
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py
priority: high
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
From a product standpoint, repository onboarding should only be used for first-time submission. If a repository has already been ingested, users should not be able to submit it again from the onboarding repository picker. Instead, the product should direct them to Repository Operations, where existing repositories are already managed through refresh and generate flows.

Implement duplicate protection across both the frontend and backend so the behavior is authoritative and user-friendly. The backend must reject duplicate submissions even if the frontend state is stale, while the frontend should proactively identify already-ingested repositories, prevent redundant submission, and show a toast with an in-app router link to Repository Operations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Onboarding clearly indicates when a repository has already been ingested and does not allow that repository to be submitted again from the repository picker
- [ ] #2 POST /start-ingestion rejects duplicate repository submissions with a duplicate-specific non-2xx response and a user-readable message
- [ ] #3 If a duplicate submission is attempted, the onboarding UI shows a toast that explains the repository is already managed and includes a clickable in-app link to Repository Operations
- [ ] #4 The navigation from the duplicate toast uses router-based in-app navigation rather than a full page reload
- [ ] #5 Repository Operations remains the canonical place to manage already-ingested repositories through refresh and generate actions
- [ ] #6 Successful first-time repository submission behavior remains intact
- [ ] #7 Duplicate prevention works for both GitHub and GitHub Enterprise providers
- [ ] #8 Automated test coverage verifies backend duplicate rejection and frontend duplicate handling behavior
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the onboarding repository picker flow and add ingested-repository query data to RepositoryDataTable so duplicate repositories can be detected before mutation.
2. Update repository row action rendering in repository-data-table-columns to visually distinguish already-ingested repositories and prevent the ingest mutation from being triggered for those rows.
3. Update duplicate error handling in RepositoryDataTable to show a toast with clear copy and a router-based link to /repositoryOperations.
4. Update the onboarding success path to invalidate the ingested-repositories query so Repository Operations sees newly submitted repositories without stale data.
5. Add a backend duplicate guard in POST /start-ingestion that checks for an existing Repository record before starting a new workflow and returns a duplicate-specific HTTP response.
6. Add or update backend tests covering initial submission and duplicate submission behavior for supported repository providers.
7. Add or update frontend tests covering disabled duplicate actions and duplicate toast/link behavior.
8. Run the relevant frontend and backend verification commands required by the repo before closing the task.

While implementing, verify the duplicate-prevention UX first in the Repository Open tab/path, then confirm the same shared flow works for GitHub Enterprise without forking the behavior by provider.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Product intent: simplify repository operations by making onboarding a first-time submission flow only. Once a repository is already present, users should be sent conceptually to Repository Operations rather than being allowed to submit it again from onboarding.

Scope note: this task should block repeat submission for repositories that already exist in the ingested repository list, not just for repositories with an active workflow run. Refresh/generate should continue to live in Repository Operations.

Implementation detail: start validation from the Repository Open onboarding flow (`ProviderKey.GITHUB_OPEN`) because it is the primary repository submission path, but land the duplicate-prevention logic in the shared repository onboarding flow so the same behavior also applies to `ProviderKey.GITHUB_ENTERPRISE`.

Provider coverage requirement: the UI and backend must not ship as `GITHUB_OPEN`-only behavior. `GITHUB_OPEN` can be the first path exercised during development and testing, but the final implementation and acceptance validation must cover both GitHub Open and GitHub Enterprise submission flows.
<!-- SECTION:NOTES:END -->
