---
id: TASK-24
title: Introduce architecture-level capability grouping for framework features
status: In Progress
assignee:
  - '@OpenCode'
created_date: '2026-03-30 04:57'
updated_date: '2026-04-03 04:55'
labels:
  - schema
  - framework-features
  - architecture
milestone: Framework feature architecture
dependencies: []
references:
  - doc-2
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/app_interfaces_mapper.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/content/docs/contribution/custom-framework-schema/index.mdx
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Architecture-level capability grouping is now documented in the public v4 schema and is mostly adopted in flow-bridge through operation-level persisted keys (`capability.operation`). Remaining work is to reconcile the public docs/examples with the simplified single-contract operation model, add real Firebase TypeScript definitions against the final capability taxonomy, and update query-engine outputs/mappers to consume capability + operation metadata instead of raw feature keys.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented design exists for separating precise detector identity from library-agnostic architectural capability grouping.
- [ ] #2 The chosen design explains whether current schema features can be grouped directly, where that approach breaks down, and what schema changes are required.
- [ ] #3 The design identifies downstream model or mapper changes needed so architectural capabilities such as authentication are not forced into library-specific internal constructs.
- [ ] #4 Firebase TypeScript support is aligned to the chosen capability-grouping approach.
<!-- AC:END -->
