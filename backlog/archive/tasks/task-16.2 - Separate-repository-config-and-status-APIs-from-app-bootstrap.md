---
id: TASK-16.2
title: Separate repository config and status APIs from app bootstrap
status: To Do
assignee: []
created_date: '2026-03-18 07:16'
labels:
  - backend
  - refactor
  - repository-config
  - task-16
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/repository_metadata_service.py
parent_task_id: TASK-16
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Give TASK-16 a clear backend home for saved repository config and workflow visibility by moving repository read and admin APIs out of `main.py` and into dedicated routers and services.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dedicated router modules own the repository config, repository status, parent workflow jobs, ingested repositories, and repository deletion endpoints currently defined in `main.py`.
- [ ] #2 Existing response models and current consumer behavior remain intact while these handlers are removed from `main.py`.
- [ ] #3 Shared mapping logic for repository, config, and status responses is extracted or reused instead of copied between handlers.
- [ ] #4 Relevant backend tests cover the moved endpoints and touched typecheck/lint checks pass.
<!-- AC:END -->
