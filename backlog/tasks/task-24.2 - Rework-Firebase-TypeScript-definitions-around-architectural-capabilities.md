---
id: TASK-24.2
title: Rework Firebase TypeScript definitions around architectural capabilities
status: In Progress
assignee:
  - '@OpenCode'
created_date: '2026-03-30 04:57'
updated_date: '2026-04-03 04:55'
labels:
  - firebase
  - typescript
  - framework-features
milestone: Framework feature architecture
dependencies:
  - TASK-24
references:
  - doc-2
documentation:
  - doc-2
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json
parent_task_id: TASK-24
priority: medium
ordinal: 1300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Firebase capability grouping is designed and documented, but the ingestion catalog does not yet ship real Firebase TypeScript definitions. Add Firebase Web SDK definitions for app bootstrap, authentication, document database, and file storage using the final capability/operation contract, while keeping ambiguous or validator-backed expansion candidates separated from direct high-confidence detections.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Firebase Phase 1 definitions use architecture-level capability naming where the schema supports it.
- [ ] #2 Related Firebase APIs that represent the same software capability are grouped only when the schema can express them safely without losing important semantics.
- [ ] #3 Validator-backed Firebase expansion candidates are identified separately from direct high-confidence capability definitions.
<!-- AC:END -->
