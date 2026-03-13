---
id: TASK-3.6.1
title: >-
  Rollback detector-side automated CallExpression score adjustments and keep
  match evidence
status: Done
assignee: []
created_date: '2026-03-06 05:58'
updated_date: '2026-03-10 09:31'
labels:
  - python
  - typescript
  - call-expression
  - confidence-scoring
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/test_framework_detection_tree_sitter.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/engine/programming_language/typescript/test_typescript_additional_concept_extraction.py
parent_task_id: TASK-3.6
priority: high
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove Python and TypeScript detector score arithmetic for CallExpression detections while preserving import-bound matcher evidence (`call_match_kind`, `matched_absolute_path`, optional `matched_alias`) and current no-suffix-fallback semantics. Keep `match_confidence` populated from the feature definition only.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Python and TypeScript detectors no longer define or use automated CallExpression score-adjustment helpers/bonus tables/ambiguity penalties.
- [x] #2 CallExpression metadata still includes match evidence fields and writes `match_confidence` equal to `spec.base_confidence`.
- [x] #3 Import-bound matching behavior and negative collision protections remain unchanged.
- [x] #4 Targeted detector tests cover manual-confidence metadata behavior and pass.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-03-06: Started rollback slice. Focus: remove detector-side CallExpression score arithmetic in Python/TypeScript while preserving evidence fields and import-bound matching semantics.

Removed detector-side CallExpression score-adjustment helpers and ambiguity-penalty arithmetic from Python and TypeScript detectors.

CallExpression metadata now preserves import-bound evidence fields and writes `match_confidence` directly from `spec.base_confidence`; renamed policy marker to `call_match_policy_version`.

Preserved import-bound/no-suffix-fallback matcher semantics and negative collision protections unchanged.

Updated targeted detector tests to assert manual-confidence behavior and evidence fields. Verification: `uv run --group dev basedpyright ...` passed, `uv run ruff check ...` passed, `uv run --group test pytest tests/parser/test_framework_detection_tree_sitter.py tests/engine/programming_language/typescript/test_typescript_additional_concept_extraction.py -v` passed (15 tests).
<!-- SECTION:NOTES:END -->
