---
id: TASK-24.3
title: Align query-engine outputs with architectural capability grouping
status: In Progress
assignee:
  - '@OpenCode'
created_date: '2026-03-30 04:57'
updated_date: '2026-04-03 04:55'
labels:
  - query-engine
  - architecture
  - framework-features
milestone: Framework feature architecture
dependencies:
  - TASK-24
references:
  - doc-2
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/app_interfaces_mapper.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json
parent_task_id: TASK-24
priority: high
ordinal: 1200
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Flow-bridge now preserves capability_key and operation_key metadata, but query-engine outputs still classify framework usages from raw feature_key strings and push unmapped capabilities into internal constructs. Update downstream models and interface mapping so architectural capabilities such as authentication, HTTP endpoints, and file storage are represented from capability/operation metadata instead of legacy flat feature keys.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Output models can represent authentication or identity-style capabilities without relying on library-specific internal construct names.
- [ ] #2 Interface mapping or framework summaries consume the new capability grouping consistently.
- [ ] #3 Tests cover at least one capability that previously fell through to internal constructs because no architectural enum existed.
<!-- AC:END -->
