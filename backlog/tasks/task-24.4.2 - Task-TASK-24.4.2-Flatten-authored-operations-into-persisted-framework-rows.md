---
id: TASK-24.4.2
title: Task TASK-24.4.2 - Flatten authored operations into persisted framework rows
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-03-30 13:14'
updated_date: '2026-04-03 04:55'
labels:
  - ingestion
  - framework-features
  - postgres
milestone: Framework feature architecture
dependencies:
  - TASK-24.4.1
references:
  - TASK-24.4
  - doc-3
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_query_service.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py
  - doc-3
parent_task_id: TASK-24.4
priority: high
ordinal: 1520
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Completed flattening of authored capability.operation definitions into persisted framework rows while preserving JSONB runtime payloads and feature_absolute_path indexing. Query reconstruction now rebuilds executable FeatureSpec objects with capability_key and operation_key populated from persisted metadata.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Framework loading flattens authored capability.operation definitions into framework_feature rows with feature_key set to capability.operation.
- [ ] #2 feature_absolute_path rows remain seeded per operation so import lookup continues to use relational indexed prefiltering.
- [ ] #3 Query reconstruction returns executable FeatureSpec objects with capability_key and operation_key populated from JSONB plus the stored absolute paths.
- [ ] #4 Loader and query tests cover flattening, JSONB preservation, and reconstructed spec parity.
<!-- AC:END -->
