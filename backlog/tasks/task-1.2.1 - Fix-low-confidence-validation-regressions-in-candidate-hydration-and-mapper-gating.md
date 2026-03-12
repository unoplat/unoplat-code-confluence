---
id: TASK-1.2.1
title: >-
  Fix low-confidence validation regressions in candidate hydration and mapper
  gating
status: Done
assignee: []
created_date: '2026-02-27 13:12'
updated_date: '2026-03-10 09:31'
labels:
  - query-engine
  - validator
  - regression
  - call-expression
  - app-interfaces
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_framework_repository.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/app_interfaces_mapper.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/app_interfaces_activity.py
  - >-
    unoplat-code-confluence-query-engine/tests/db/test_framework_feature_validation_repository.py
  - >-
    unoplat-code-confluence-query-engine/tests/services/repository/test_app_interfaces_mapper.py
documentation:
  - 'backlog://workflow/overview'
  - >-
    unoplat-code-confluence-query-engine/backlog/docs/doc-006 -
    CallExpression-Confidence-Scoring-and-Validation-Agent.md
parent_task_id: TASK-1.2
priority: high
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Address review-discovered regressions introduced in TASK-1.2 that can break validator execution at runtime and allow contradictory or partially validated framework rows into app-interface output.

Problem flow (why current behavior is wrong)
1. Candidate fetch returns ORM-backed `FrameworkFeature` records for low-confidence CallExpression rows.
2. Candidate DTO construction happens after the DB session context is closed.
3. Accessing `feature.absolute_paths` at that point can lazy-load on a detached ORM instance, raising `DetachedInstanceError`.
4. Even when attached, `absolute_paths` is a list of `FeatureAbsolutePath` ORM objects, but candidate model expects `list[str]`; this can fail model validation and block validator workflow.
5. Mapper inclusion logic currently allows rows with confidence >= 0.70 before enforcing completed validation status, so rows can leak into output while still `pending` if confidence write succeeds but status transition fails/retries.
6. `correct` decisions currently keep the source row eligible for inclusion while also writing corrected row data, producing contradictory duplicate classifications for the same file/span.

Impact
- Runtime failures in low-confidence candidate fetching/validation execution.
- Incorrect app-interface aggregation due to stale, duplicated, or partially validated rows.
- Violates intended two-step validation protocol (evidence/confidence write + status transition gate).

Target outcome
- Low-confidence validation candidate fetch is session-safe and type-safe.
- Mapper inclusion requires completed validation semantics for revalidated rows.
- `correct` decisions replace source classification behavior in output (while preserving original audit trail).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Low-confidence candidate retrieval does not access lazy ORM fields after session close, and `absolute_paths` is provided to candidate models as `list[str]` in all cases.
- [ ] #2 Candidate building path is covered by a regression test that would fail on detached-instance access or non-string absolute path payloads.
- [ ] #3 Rows that have been revalidated are only included in app-interface mapping when validation status is `completed`; confidence alone is insufficient for inclusion.
- [ ] #4 `correct` validation decisions do not leave the original misclassified source row eligible for mapper inclusion in final app-interface output.
- [ ] #5 Mapper/regression tests cover: (a) pending+high-confidence row exclusion, (b) confirm inclusion after completed status, (c) correct replaces source key behavior without contradictory duplicates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
If requested, run the full validator repository/tool test suite and close TASK-1.2.1 after user validation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Patched repository gating + candidate hydration regressions from review.

`db_get_low_confidence_call_expression_candidates` now eager-loads `FrameworkFeature.absolute_paths` and materializes candidates inside active session scope; `absolute_paths` is converted to `list[str]` via `FeatureAbsolutePath.absolute_path` before model construction.

`_should_include_in_app_interface_mapping` now gates any row with validator decision on `validation_status == completed` and accepts only `confirm` decisions for inclusion (source rows with `correct` are excluded).

Added DB regression coverage in `tests/db/test_framework_feature_validation_repository.py` for: candidate absolute path typing, pending+high-confidence revalidated row exclusion, and `correct` source-row exclusion with corrected-row inclusion.

Verification run: `uv run python -m pytest tests/db/test_framework_feature_validation_repository.py -k "low_confidence_candidate_query_returns_pending_call_expression_only or app_interface_fetch_excludes_low_confidence_call_expression_until_completed or app_interface_fetch_excludes_revalidated_pending_row_even_if_confidence_high or app_interface_fetch_excludes_source_row_after_correct_decision" -v` => 4 passed.
<!-- SECTION:NOTES:END -->
