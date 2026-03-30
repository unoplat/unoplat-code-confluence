---
id: TASK-24
title: Introduce architecture-level capability grouping for framework features
status: In Progress
assignee:
  - OpenCode
created_date: '2026-03-30 04:57'
updated_date: '2026-03-30 06:31'
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
Framework feature definitions currently use feature keys as the main semantic label, which pushes us toward library-specific names like `get_auth` instead of software-engineering fundamentals like app bootstrap, authentication, document database access, or file storage. We need a design that preserves precise detection while also supporting library-agnostic capability grouping so downstream outputs can aggregate by architectural intent rather than raw API names.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented design exists for separating precise detector identity from library-agnostic architectural capability grouping.
- [ ] #2 The chosen design explains whether current schema features can be grouped directly, where that approach breaks down, and what schema changes are required.
- [ ] #3 The design identifies downstream model or mapper changes needed so architectural capabilities such as authentication are not forced into library-specific internal constructs.
- [ ] #4 Firebase TypeScript support is aligned to the chosen capability-grouping approach.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Publish DIDS v4 in `unoplat-code-confluence-docs` as the design source of truth for architecture-level grouping.
2. Use library-level `capabilities`, capability-level `operations`, and operation-level `detectors` so one capability can contain multiple operations and each operation can contain multiple precise detectors or variants.
3. Keep precise match semantics on detectors: `absolute_paths`, `target_level`, `concept`, `construct_query`, `base_confidence`, and low-confidence `notes` constraints remain detector-scoped.
4. Introduce enum validation for capability families and operation kinds, while detector keys remain contributor-defined identifiers local to each operation.
5. After the docs schema is stable, implement ingestion-side schema/model/test changes, then update Firebase definitions to the new structure, then align query-engine aggregation and output mapping to capability + operation instead of raw feature keys.
6. Use FastAPI route methods and Firebase auth sign-in flows as validation examples for grouping: `http_endpoint -> register_handler -> get/post/...` and `authentication -> sign_in -> email_password/popup/redirect`.
7. Preserve v3 as legacy documentation during migration; keep latest schema alias pointed at v4 once the docs page is updated.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Docs-first v4 direction chosen: publish a breaking schema version that replaces flat `features` with `capabilities -> operations -> detectors`. Capability and operation keys become enum-validated architectural groupings; detector keys preserve precise matching identity and carry `absolute_paths`, `concept`, `target_level`, `construct_query`, and `base_confidence`.
<!-- SECTION:NOTES:END -->
