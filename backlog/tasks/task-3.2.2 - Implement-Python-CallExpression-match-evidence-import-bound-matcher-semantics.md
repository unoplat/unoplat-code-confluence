---
id: TASK-3.2.2
title: >-
  Implement Python CallExpression match evidence + import-bound matcher
  semantics
status: Done
assignee: []
created_date: '2026-03-05 09:56'
updated_date: '2026-03-10 09:31'
labels:
  - python
  - framework-detection
  - call-expression
  - confidence-scoring
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/test_framework_detection_tree_sitter.py
parent_task_id: TASK-3.2
priority: high
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the Python detector portion of TASK-3.2 by replacing boolean callee matching with a typed evidence return model, removing suffix/member fallback heuristics, and keeping detection behavior strictly import-bound. Include deterministic match_kind classification for exact symbol/alias/module-member outcomes and no_match.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Python `_matches_callee(...)` returns typed match evidence (not bool) with fields needed by deterministic scoring.
- [x] #2 Python CallExpression matching no longer accepts `endswith(...)` suffix/member fallback paths.
- [x] #3 Match evidence classifies import-bound exact outcomes and no-match outcomes with stable `match_kind` literals.
- [x] #4 Existing valid import-bound Python CallExpression detections remain detected after refactor.
- [x] #5 Python detector tests cover positive import-bound match and negative unrelated-member collision case.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-03-05: Started execution as first implementation slice for TASK-3.2. Focus: replace bool matcher with typed evidence and enforce import-bound call matching with no suffix fallback.

Implemented typed CallExpression match evidence in Python detector (`CallMatchEvidence` + `CallMatchKind`) and switched `_matches_callee(...)` to return evidence object.

Removed suffix/member fallback acceptance for Python CallExpression matching; matching is now import-bound exact via symbol alias, module alias + member, or root-module alias + member.

Updated call-expression detection path to gate on `call_match_evidence.matched` instead of boolean matcher return.

Added regression tests in `tests/parser/test_framework_detection_tree_sitter.py` for: (1) import-bound module-alias positive case (`llm.completion`), (2) unrelated member collision negative case (`api.completion(...)`).

Verification run: `uv run --group dev basedpyright src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py tests/parser/test_framework_detection_tree_sitter.py` (pass), `uv run ruff check ...` (pass), `uv run --group test pytest tests/parser/test_framework_detection_tree_sitter.py -v` (7 passed).
<!-- SECTION:NOTES:END -->
