---
id: TASK-16.9.3
title: >-
  Ingestion: propagate monorepo metadata through child workflows and package
  metadata ingestion
status: To Do
assignee: []
created_date: '2026-03-23 07:06'
updated_date: '2026-03-23 07:10'
labels:
  - backend
  - typescript
  - monorepo
  - ingestion
  - workflow
  - bug
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
Ensure package_manager_provenance, workspace_root, manifest_path, and project_name survive ingestion workflow handoff paths so child workflows and downstream processors do not reconstruct TypeScript workspaces as standalone local projects.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Child workflow payloads preserve package_manager_provenance, workspace_root, manifest_path, and project_name for TypeScript workspaces.
- [ ] #2 `codebase_child_workflow.py` does not reconstruct `ProgrammingLanguageMetadata` in a way that drops monorepo ownership fields.
- [ ] #3 Downstream package metadata ingestion and relational persistence consume those fields without reclassifying inherited workspaces as standalone local projects.
- [ ] #4 An inherited-workspace regression proves the metadata survives end to end from repository ingestion through child workflow handoff.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Audit all ingestion workflow envelopes and model reconstruction points where `ProgrammingLanguageMetadata` is rebuilt.
2. Preserve the new monorepo fields through child workflow handoff and package metadata activities.
3. Confirm database persistence paths keep those fields intact for later query-engine consumption.
4. Add focused regression coverage for an inherited workspace case that previously degraded to local standalone metadata.
<!-- SECTION:PLAN:END -->
