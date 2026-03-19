---
id: TASK-16.1
title: Validate the end-to-end TASK-16 alpha flow
status: To Do
assignee: []
created_date: '2026-03-18 07:15'
updated_date: '2026-03-19 09:57'
labels:
  - integration
  - testing
  - alpha
  - task-16
dependencies:
  - TASK-16.2
  - TASK-16.7
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-frontend/src/components/custom/RepositoryDataTable.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/IngestedRepositoriesDataTable.tsx
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/typescript_ripgrep_detector.py
parent_task_id: TASK-16
priority: high
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Close TASK-16 with an integration-focused validation pass that proves the alpha codebase-configuration experience works across backend APIs, detection, persistence, and frontend screens.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Integration-oriented coverage validates detection preview, `Ingest All`, reviewed subset ingestion, saved-config viewing and reuse, and explicit re-detect replacement.
- [ ] #2 End-to-end behavior confirms saved approved config remains canonical for repository operations until replacement.
- [ ] #3 Final task notes capture any accepted alpha limitations and reference the completed subtasks that delivered the flow.
- [ ] #4 Cross-cutting diagnostics for touched frontend and backend code pass before TASK-16 is closed.
<!-- AC:END -->
