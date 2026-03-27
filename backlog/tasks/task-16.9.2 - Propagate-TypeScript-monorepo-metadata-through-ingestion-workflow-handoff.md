---
id: TASK-16.9.2
title: Propagate TypeScript monorepo metadata through ingestion workflow handoff
status: To Do
assignee: []
created_date: '2026-03-23 11:13'
labels:
  - backend
  - typescript
  - monorepo
  - ingestion
  - workflow
  - task-16
dependencies:
  - TASK-16.9.1
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/repo_workflow.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/codebase_child_workflow.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/package_metadata_activity/package_manager_metadata_activity.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/package_metadata_activity/package_manager_metadata_ingestion.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py
parent_task_id: TASK-16.9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure ingestion workflow payloads and child-workflow reconstruction preserve TypeScript monorepo ownership metadata end to end. This task covers the handoff path after workspace discovery so inherited workspaces do not degrade into standalone local projects before persistence and downstream package metadata processing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Child-workflow payloads preserve package_manager_provenance, workspace_root, manifest_path, project_name, and any new workspace discovery metadata needed by downstream consumers.
- [ ] #2 ProgrammingLanguageMetadata is not reconstructed in ingestion workflow code paths in a way that drops or defaults monorepo ownership fields.
- [ ] #3 Downstream package metadata ingestion and persistence keep inherited workspace metadata intact rather than reclassifying inherited workspaces as local standalone projects.
- [ ] #4 Regression coverage proves an inherited workspace case survives from detector output through workflow handoff and persistence.
<!-- AC:END -->
