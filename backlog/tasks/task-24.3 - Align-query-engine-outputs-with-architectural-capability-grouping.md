---
id: TASK-24.3
title: Align query-engine outputs with architectural capability grouping
status: To Do
assignee:
  - OpenCode
created_date: '2026-03-30 04:57'
updated_date: '2026-03-30 06:32'
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
Update downstream output and mapping models so framework detections can be aggregated by architectural capability instead of exposing only library-specific feature keys. This includes resolving the current gap where authentication-like capabilities do not have a clean architectural home in output models.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Output models can represent authentication or identity-style capabilities without relying on library-specific internal construct names.
- [ ] #2 Interface mapping or framework summaries consume the new capability grouping consistently.
- [ ] #3 Tests cover at least one capability that previously fell through to internal constructs because no architectural enum existed.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add architectural grouping inputs to the query-engine ingestion path so feature usages carry capability family, operation kind, and precise detector identity.
2. Refactor `app_interfaces_mapper.py` to map architectural capability families and operations rather than hard-coded raw feature keys where possible.
3. Extend output models so authentication or identity-style capabilities have a first-class representation instead of falling through to `InternalConstruct.kind = feature_key`.
4. Decide where verb or variant qualifiers belong in outputs for cases like `http_endpoint -> register_handler -> get/post` without exploding top-level enums unnecessarily.
5. Keep detector identity available in evidence or match metadata so debugging and validator workflows still retain the exact matched symbol.
6. Add regression coverage for at least one previously unmapped capability, such as authentication, and one grouped capability with variants, such as HTTP route handlers by verb.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Planned against the v4 hierarchy. Query-engine aggregation should stop treating raw detector keys as architectural kinds and instead consume capability + operation metadata, with detector keys reserved for precision and evidence.
<!-- SECTION:NOTES:END -->
