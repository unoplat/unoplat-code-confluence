---
id: TASK-24.4.5
title: >-
  Simplify operation schema around single-contract operations before continuing
  migration
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-04-01 04:55'
updated_date: '2026-04-03 04:55'
labels:
  - framework-features
  - schema
  - docs
  - commons
  - ingestion
milestone: Framework feature architecture
dependencies: []
references:
  - doc-3
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/backlog/docs/doc-3
    - Flow-Bridge-v4-Operation-Key-Migration-Design.md
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat_code_confluence_commons/src/unoplat_code_confluence_commons/base_models/engine_models.py
parent_task_id: TASK-24.4
priority: high
ordinal: 1510
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Completed the no-variants simplification across public docs, commons, and flow-bridge so each operation represents one executable runtime contract. Future first-class variant support remains explicitly deferred until a concrete use case exists.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Public docs and schema guidance describe operations as single executable runtime contracts and do not imply first-class variant support.
- [ ] #2 Shared commons models and tests align with single-contract operation payloads while preserving operation metadata round-trip and current validation rules.
- [ ] #3 Flow-bridge ingestion schema, fixtures, and regressions align with the simplified single-contract operation model before the broader migration continues.
- [ ] #4 Any future variant support is explicitly deferred and documented as out of scope until a real use case exists.
<!-- AC:END -->
