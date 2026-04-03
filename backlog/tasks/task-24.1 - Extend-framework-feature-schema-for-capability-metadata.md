---
id: TASK-24.1
title: Extend framework feature schema for capability metadata
status: In Progress
assignee:
  - '@OpenCode'
created_date: '2026-03-30 04:57'
updated_date: '2026-04-03 04:55'
labels:
  - schema
  - framework-features
milestone: Framework feature architecture
dependencies:
  - TASK-24
references:
  - doc-2
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/content/docs/contribution/custom-framework-schema/index.mdx
parent_task_id: TASK-24
priority: high
ordinal: 1100
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The public v4 schema and docs direction are in place, but schema alignment is not fully finished. We still need to reconcile the contributor-facing examples and wording with the simplified single-contract operation model and ensure ingestion-side schema/taxonomy parity for capability families needed by Firebase-style definitions such as authentication, document_db, file_storage, and app_bootstrap.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The schema supports explicit architectural capability metadata separate from absolute-path detection identity.
- [ ] #2 The schema design documents whether operation-level grouping is also supported and how grouped features remain valid for CallExpression validation.
- [ ] #3 Schema validation tests cover the new metadata fields and reject invalid values.
<!-- AC:END -->
