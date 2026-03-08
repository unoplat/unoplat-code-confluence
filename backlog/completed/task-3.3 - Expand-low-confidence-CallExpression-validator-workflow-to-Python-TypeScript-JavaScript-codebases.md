---
id: TASK-3.3
title: >-
  Expand low-confidence CallExpression validator workflow to Python +
  TypeScript/JavaScript codebases
status: Done
assignee: []
created_date: '2026-03-04 10:56'
updated_date: '2026-03-07 12:25'
labels:
  - query-engine
  - validator
  - typescript
  - javascript
  - workflow
dependencies:
  - TASK-3.2
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/app_interfaces_activity.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_framework_repository.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/event_stream_handler.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/dependency_guide_completion_activity.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/engineering_workflow_completion_activity.py
  - >-
    unoplat-code-confluence-query-engine/tests/db/test_framework_feature_validation_repository.py
  - >-
    unoplat-code-confluence-query-engine/tests/tools/test_framework_feature_validation_tools.py
documentation:
  - >-
    unoplat-code-confluence-query-engine/backlog/docs/doc-006 -
    CallExpression-Confidence-Scoring-and-Validation-Agent.md
parent_task_id: TASK-3
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context
Query-engine currently executes low-confidence CallExpression validation only when codebase language is Python, leaving TypeScript/JavaScript ecosystem codepaths unvalidated before app-interface mapping.

## Goal
Run the existing call_expression_validator pipeline for all currently supported framework-detection languages in app-interfaces flow, including TypeScript and JavaScript-identified codebases (normalized to TypeScript framework feature language where needed).

## Scope
- Temporal workflow app-interface branch and candidate-fetch step
- Activity/repository language handling and JavaScript->TypeScript normalization
- Completion namespace/progress tracking behavior
- Tests for TypeScript and JavaScript-normalized validation gating

## Out of Scope
- New .js/.jsx parser implementation in ingestion
- Non-CallExpression concept validation
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CodebaseAgentWorkflow no longer hard-gates app_interfaces + low-confidence validator execution to Python-only.
- [ ] #2 TypeScript codebases execute low-confidence candidate fetch + call_expression_validator + app-interface build in the same sequence as Python.
- [ ] #3 JavaScript codebases in query-engine workflow are normalized to existing TypeScript framework-feature language for candidate fetch and app-interface reads (without introducing new parser scope).
- [ ] #4 Repository query functions return low-confidence candidates for TypeScript rows with concept=CallExpression and confidence below threshold.
- [ ] #5 App-interface mapping excludes low-confidence TypeScript/JavaScript-normalized CallExpression rows until validator decision/status acceptance policy is met.
- [ ] #6 Completion namespace/progress logic treats app_interfaces_agent completion consistently for TypeScript/JavaScript codebases (not Python-exclusive).
- [ ] #7 Existing Python validator behavior remains unchanged.
- [ ] #8 Targeted repository/workflow/activity tests cover Python + TypeScript + JavaScript-normalized paths and pass.
- [ ] #9 Query-engine typecheck then lint then targeted tests pass for touched files/suites.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1) Remove Python-only workflow gate for app-interfaces stage.
- Refactor `CodebaseAgentWorkflow` app-interfaces section in `temporal_workflows.py` so low-confidence fetch + validator + app-interface build runs for supported languages (`python`, `typescript`, `javascript`).
- Keep explicit skip branch for unsupported languages with clear log message.

2) Add language normalization for framework-feature reads.
- Implement shared normalization helper (module-level, reusable) mapping `javascript -> typescript` for framework feature repository queries.
- Apply normalization in:
  - `AppInterfacesActivity.fetch_low_confidence_call_expression_candidates(...)`
  - `AppInterfacesActivity.build_app_interfaces(...)`
  - repository functions `db_get_low_confidence_call_expression_candidates(...)` and `db_get_all_framework_features_for_codebase(...)`.
- Preserve Python behavior unchanged.

3) Keep validator contract and gating semantics unchanged.
- Reuse existing candidate predicate (`concept=CallExpression`, low confidence, status pending/needs_review).
- Reuse existing decision/status policy (`confirm/correct` completed rows included; reject/needs_review excluded).

4) Expand progress/completion namespace behavior.
- Update `get_completion_namespaces(...)` in `event_stream_handler.py` so `app_interfaces_agent` counts for TypeScript and JavaScript codebases, not only Python.
- Ensure dependency and engineering completion activities inherit updated namespaces without additional API changes.

5) Add tests for cross-language workflow data paths.
- Repository tests: verify TypeScript low-confidence candidate fetch and JavaScript-normalized lookup behavior.
- Progress helper tests: verify completion namespaces include `app_interfaces_agent` for python/typescript/javascript.
- Add focused tests for workflow language gating logic if extracted into pure helper function.

6) Verification.
- Run query-engine checks in order: typecheck -> lint -> targeted pytest for updated DB/activity/helper tests.
- Confirm no regressions for existing Python validator path.

Implementation detail to adopt: define a shared supported-language set for the app-interfaces + low-confidence validator stage instead of an inline Python-only conditional. Recommended shape is a module-level constant/helper that checks normalized framework-feature language membership so Python and TypeScript both run the validator path, with JavaScript handled through existing normalization rather than duplicated branch logic.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-03-06: Added child task TASK-3.3.1 to improve the CallExpression validator instructions with explicit candidate metadata fields, docs-first review order, and metadata-vs-code gap analysis guidance.

Implemented TASK-3.3.1 prompt improvement slice: validator prompt is now metadata-aware and docs-first, with explicit guidance on candidate fields, evidence_json keys, and gap recording before evidence/status writes.

2026-03-07 investigation confirmed the workflow is still hard-gated by `if codebase_metadata.codebase_programming_language.lower() == "python"` in `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py`, so TypeScript codebases cannot currently enter validator/app-interfaces flow even though repository/activity code is otherwise language-parameterized.

Agreed implementation direction: replace the Python-only check with a supported-language set plus normalization helper, enabling the validator/app-interfaces path for Python and TypeScript explicitly and keeping JavaScript handled via normalization to TypeScript framework-feature language.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## Summary

Expanded the low-confidence CallExpression validator workflow from Python-only to Python + TypeScript.

### Changes

| File | Action | Key Change |
|------|--------|-----------|
| `utils/framework_feature_language_support.py` | CREATE | `APP_INTERFACES_SUPPORTED_LANGUAGES` frozenset + `is_app_interfaces_supported()` helper |
| `services/temporal/temporal_workflows.py` | EDIT | Replaced `== "python"` gate with `is_app_interfaces_supported()` |
| `services/temporal/event_stream_handler.py` | EDIT | Replaced `language == "python"` namespace check with `is_app_interfaces_supported()` |
| `tests/utils/test_framework_feature_language_support.py` | CREATE | 7 unit tests (supported/unsupported/case-insensitive) |
| `tests/db/test_framework_feature_validation_repository.py` | EDIT | New low-confidence TS fixture + 2 integration tests |

### Verification

- Typecheck: 0 errors on changed files
- Lint: all checks passed
- Unit tests: 7/7 passed
- Integration tests: 10/10 passed (8 existing + 2 new)
<!-- SECTION:FINAL_SUMMARY:END -->
