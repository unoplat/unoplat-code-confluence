---
id: TASK-29
title: Continue OpenMetadata connector sandbox pre-flight
status: In Progress
assignee: []
created_date: '2026-04-26 04:50'
labels:
  - openmetadata
  - connector
milestone: OpenMetadata connector
dependencies: []
references:
  - PLAN-openmetadata-connector.md
priority: medium
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Continue the Code Confluence to OpenMetadata connector work from PLAN-openmetadata-connector.md so the connector can rely on latest completed query-engine snapshots and be prepared for local sandbox ingestion against an existing repository result for unoplat/unoplat-code-confluence.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Connector config allows repositoryWorkflowRunId to be omitted while preserving explicit run id support.
- [ ] #2 Connector HTTP client omits repository_workflow_run_id from query params when no run id is configured.
- [ ] #3 Query-engine snapshot endpoint tests cover exact run id, latest completed selection, 404 for no completed snapshot, and skipping non-COMPLETED runs.
- [ ] #4 Relevant typecheck and lint/test commands are run or blockers are documented.
<!-- AC:END -->
