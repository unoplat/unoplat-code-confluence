---
id: TASK-24.4.1
title: Extend flow-bridge schema and shared models for operation metadata
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-03-30 13:14'
updated_date: '2026-03-30 13:50'
labels:
  - ingestion
  - framework-features
  - schema
  - commons
milestone: Framework feature architecture
dependencies:
  - TASK-24.1
references:
  - TASK-24.4
  - doc-3
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py
  - doc-3
parent_task_id: TASK-24.4
priority: high
ordinal: 1510
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable flow-bridge framework definitions to be authored in capability/operation form while shared typed models can round-trip operation metadata through JSONB without changing the phase-1 relational table layout.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Flow-bridge framework-definition schema accepts authored capability blocks with nested operations and enforces one operation payload per executable runtime contract.
- [x] #2 Shared typed models can round-trip capability_key and operation_key alongside the existing runtime fields stored in framework_feature.feature_definition JSONB.
- [x] #3 Model-level tests cover valid operation metadata and preserve current base_confidence validation rules.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update flow-bridge framework-definitions/schema.json from flat library.features to authored library.capabilities.<capability>.operations.<operation> while preserving the existing runtime payload fields on each operation.
2. Extend commons FeatureSpec and FrameworkFeaturePayload in engine_models.py with optional capability_key and operation_key fields so JSONB payloads and reconstructed runtime specs can retain operation metadata.
3. Do not add new property wrappers for those fields on the Pydantic models. Access them directly as normal BaseModel fields.
4. Keep framework_models.py changes minimal in this subtask; avoid adding ORM convenience properties for capability_key and operation_key unless later implementation proves they are necessary.
5. Add or update commons/model tests to prove operation metadata round-trips and that current base_confidence validation still behaves the same for CallExpression payloads.
6. Keep scope limited to schema/model changes only; no loader/query/definition migration work in this subtask.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed subtask. Files changed: flow-bridge framework-definitions/schema.json, commons engine_models.py, commons tests/test_engine_models.py. Also corrected schema `$id` from the stale v3 path to the v4 path so the local schema metadata matches the new capability/operation structure.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated the local flow-bridge schema contract from flat `features` to authored `capabilities -> operations`, added plain optional `capability_key` and `operation_key` fields to the shared Pydantic models, and added focused commons tests to prove operation metadata round-trips without changing existing `base_confidence` validation behavior.

Validation: `uv run ruff check src/unoplat_code_confluence_commons/base_models/engine_models.py tests/test_engine_models.py` and `uv run pytest tests/test_engine_models.py` in `unoplat-code-confluence-commons` passed. `uv run basedpyright ...` was attempted there but the commons environment does not currently provide `basedpyright`.
<!-- SECTION:FINAL_SUMMARY:END -->
