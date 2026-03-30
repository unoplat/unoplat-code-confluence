---
id: TASK-24.1
title: Extend framework feature schema for capability metadata
status: In Progress
assignee:
  - OpenCode
created_date: '2026-03-30 04:57'
updated_date: '2026-03-30 06:32'
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
Update the framework definition schema so a feature can keep precise detection identity while also carrying a library-agnostic architectural capability classification. The design should avoid forcing broad capability rollups into raw feature keys alone.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The schema supports explicit architectural capability metadata separate from absolute-path detection identity.
- [ ] #2 The schema design documents whether operation-level grouping is also supported and how grouped features remain valid for CallExpression validation.
- [ ] #3 Schema validation tests cover the new metadata fields and reject invalid values.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Publish `custom-framework-lib-schema-v4.json` in docs and repoint `custom-framework-lib-schema.json` to the v4 content.
2. Replace flat `features` with `capabilities` at the library level.
3. Validate capability keys against a curated `capabilityFamilyEnum` and operation keys against `operationKindEnum`.
4. Define `capabilityDef` with `description`, optional `docs_url`, and required `operations`.
5. Define `operationDef` with `description`, optional `docs_url`, optional `startpoint`, optional `notes`, and required `detectors`.
6. Define `detectorDef` as the precise matching contract: required `absolute_paths`, `target_level`, and `concept`; optional `description`, `docs_url`, `construct_query`, `base_confidence`, and `notes`.
7. Preserve v3 validation behavior at the detector level: `CallExpression` requires `target_level=function` and `base_confidence`; low-confidence call-expression detectors require non-empty `notes`; `Inheritance` requires `target_level=class`; `FunctionDefinition` requires `target_level=function`.
8. Update the docs page to explain the new hierarchy, detector identity vs architectural grouping, and legacy v3 compatibility notes.
9. Use FastAPI as the concrete v4 example: `http_endpoint -> register_handler -> get/post/...`, and call out router composition separately so `include_router` is no longer conflated with endpoint registration.
10. After docs publication, ingestion-side implementation should derive a stable internal key from capability + operation + detector and add schema validation tests for valid and invalid enum/key combinations.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Docs-first v4 implementation will be used to lock the structure before ingestion-side adoption. The proposed breaking change is `library.features` -> `library.capabilities -> operations -> detectors`, with enum validation on capability and operation keys and detector-local validation rules preserved from v3.
<!-- SECTION:NOTES:END -->
