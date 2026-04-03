---
id: TASK-24.4.3
title: >-
  Migrate shipped framework definitions and detection expectations to operation
  keys
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-03-30 13:14'
updated_date: '2026-04-03 04:55'
labels:
  - ingestion
  - framework-features
  - definitions
  - detection
milestone: Framework feature architecture
dependencies:
  - TASK-24.4.2
references:
  - TASK-24.4
  - doc-3
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/fastapi.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/nextjs.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/code_confluence_codebase_parser.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/test_framework_detection_tree_sitter.py
  - doc-3
parent_task_id: TASK-24.4
priority: high
ordinal: 1530
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Completed migration of the shipped flow-bridge framework-definition corpus and representative detector/parser expectations to operation-level feature keys. FastAPI and Next.js now serve as regression anchors for per-operation HTTP endpoint identity.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All shipped flow-bridge framework definition JSON files load under the capability/operation authoring shape used by the updated ingestion schema.
- [ ] #2 FastAPI and Next.js definitions emit precise operation keys for representative HTTP endpoint and router-composition behaviors.
- [ ] #3 Targeted parser and detector regressions use operation-level feature_key values and do not skip known features because of catalog mismatch.
<!-- AC:END -->
