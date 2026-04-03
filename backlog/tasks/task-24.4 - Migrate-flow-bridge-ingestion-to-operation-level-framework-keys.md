---
id: TASK-24.4
title: Migrate flow-bridge ingestion to operation-level framework keys
status: In Progress
assignee:
  - '@OpenCode'
created_date: '2026-03-30 12:44'
updated_date: '2026-04-03 04:55'
labels:
  - ingestion
  - framework-features
  - schema
  - postgres
milestone: Framework feature architecture
dependencies:
  - TASK-24.1
references:
  - doc-3
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_query_service.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/code_confluence_codebase_parser.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py
  - doc-3
parent_task_id: TASK-24
priority: high
ordinal: 1500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The flow-bridge operation-key migration is substantially complete: schema/models, operation-level persistence, shipped framework-definition fixtures, and focused regressions now use capability -> operation authoring with persisted feature_key = capability.operation. Remaining work is to finish verification bookkeeping, capture residual downstream legacy-key coupling explicitly, and close the ingestion-side migration cleanly under the parent task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Ingestion framework definitions support the v4 capability/operation authoring shape and flatten operation rows into persisted framework features keyed as `capability.operation`.
- [x] #2 Shared typed models round-trip operation-level metadata through `framework_feature.feature_definition` JSONB without requiring a phase-1 PostgreSQL table redesign.
- [ ] #3 The framework loader and query service preserve indexed absolute-path prefiltering and rebuild executable runtime specs from stored operation rows.
- [ ] #4 Codebase parsing and file-feature ingestion continue to store and validate detections using stable operation-level `feature_key` values.
- [ ] #5 Representative ingestion tests cover valid operation-key flattening, schema validation, and regression behavior for at least FastAPI or Next.js.
<!-- AC:END -->
