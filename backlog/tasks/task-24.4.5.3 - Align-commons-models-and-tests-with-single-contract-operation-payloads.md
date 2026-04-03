---
id: TASK-24.4.5.3
title: Align commons models and tests with single-contract operation payloads
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-04-01 04:55'
updated_date: '2026-04-01 05:56'
labels:
  - framework-features
  - schema
  - commons
  - tests
milestone: Framework feature architecture
dependencies: []
references:
  - doc-3
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-commons/tests/test_engine_models.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/backlog/docs/doc-3
    - Flow-Bridge-v4-Operation-Key-Migration-Design.md
parent_task_id: TASK-24.4.5
priority: high
ordinal: 1512
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Review the shared commons models and regression tests introduced for operation metadata and simplify them to the no-variants decision. Preserve the current operation metadata round-trip, base confidence validation, and typed runtime reconstruction expectations, but avoid adding or retaining abstractions that suggest multiple detector variants per operation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Shared commons models reflect a single payload contract per operation while preserving capability and operation metadata round-trip.
- [x] #2 Commons regression tests cover the simplified single-contract model and preserve existing validation behavior for concepts and base confidence.
- [x] #3 No new commons abstraction implies first-class per-operation variants without a concrete use case.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the current commons payload and persisted-model surfaces in engine_models.py and framework_models.py.
2. Simplify or align the shared payload contract so one operation corresponds to one executable runtime contract with flat runtime fields.
3. Update regression coverage in test_engine_models.py to verify flat operation metadata round-trip, construct_query typing, and base_confidence validation under the single-contract model.
4. Keep changes minimal and avoid widening the public export surface unless it is strictly necessary for this task.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
This task should list direct commons edit targets only. Current expected modification files are engine_models.py, framework_models.py, and test_engine_models.py. Optional review-only surfaces are base_models/__init__.py and the package root __init__.py if export alignment becomes necessary, but they are not primary edit targets. Key policy decision remains: do not introduce first-class variants now; each operation should represent one executable runtime contract. Commons should keep detector/runtime fields directly on the flat operation payload and should not add or preserve plural detector or variant collections. Implementation decisions made: FrameworkFeaturePayload now uses extra='forbid' to align with the tightened public schema and avoid silently admitting deprecated plural payload fields; FrameworkFeature gained explicit capability_key and operation_key accessors as small flat helpers rather than any new wrapper abstraction. Verification completed with `uv run --with mypy mypy src tests/test_engine_models.py`, `uv run pytest tests/test_engine_models.py`, and `uv run ruff check src/unoplat_code_confluence_commons/base_models/engine_models.py src/unoplat_code_confluence_commons/base_models/framework_models.py tests/test_engine_models.py`. Existing SQLAlchemy mapper warnings from pytest were left untouched because they predate this task.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aligned the commons payload contract to the no-variants decision by keeping runtime fields flat on the operation payload and forbidding unknown payload keys in FrameworkFeaturePayload.

Added small FrameworkFeature capability_key and operation_key accessors so persisted JSONB helpers line up with the flat single-contract payload shape.

Updated commons regression coverage for flat operation metadata round-trip while preserving construct_query typing and base_confidence validation behavior.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 FeatureSpec and FrameworkFeaturePayload reflect a flat single-contract operation payload and do not introduce variant-style abstractions.
- [x] #2 Commons persisted payload handling in framework_models.py aligns with the same flat operation payload shape.
- [x] #3 Regression coverage verifies capability and operation metadata round-trip for single-contract operations.
- [x] #4 Regression coverage preserves construct_query typing and base_confidence validation behavior.
- [x] #5 Commons tests and model wording do not imply plural detector contracts or multiple runtime variants per operation.
- [x] #6 feature_key remains compatible with operation-level identity without changing persisted usage semantics.
<!-- DOD:END -->
