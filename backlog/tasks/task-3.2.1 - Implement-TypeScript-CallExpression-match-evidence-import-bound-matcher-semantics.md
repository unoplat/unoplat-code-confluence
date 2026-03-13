---
id: TASK-3.2.1
title: >-
  Implement TypeScript CallExpression match evidence + import-bound matcher
  semantics
status: Done
assignee: []
created_date: '2026-03-05 09:56'
updated_date: '2026-03-10 09:31'
labels:
  - typescript
  - framework-detection
  - call-expression
  - confidence-scoring
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/engine/programming_language/typescript/test_typescript_additional_concept_extraction.py
parent_task_id: TASK-3.2
priority: high
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the TypeScript detector portion of TASK-3.2 by replacing boolean callee matching with typed evidence, removing suffix/member fallback heuristics, and preserving import-bound exact matching including default import path handling for `*.default` absolute paths.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 TypeScript `_matches_callee(...)` returns typed match evidence (not bool) with deterministic `match_kind` values.
- [x] #2 TypeScript CallExpression matching removes `endswith(...)` suffix/member fallback acceptance.
- [x] #3 Default-import matching for absolute paths ending in `.default` is explicitly supported via import-bound evidence.
- [x] #4 Known collision scenario (`api.createStore(...)` with unrelated object qualifier) does not match framework feature.
- [x] #5 TypeScript tests cover positive import-bound/default-import match and negative collision case.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-03-05: Started TypeScript matcher evidence/import-bound implementation. Focus: `_matches_callee(...)` typed evidence return, no suffix/member fallback, explicit default-import evidence path.

Implemented TypeScript typed matcher evidence (`CallMatchEvidence` + `CallMatchKind`) and changed `_matches_callee(...)` return type from bool to evidence object.

Removed suffix/member fallback acceptance for CallExpression matching (`endswith(...)` paths are no longer accepted).

Preserved explicit default-import handling for `*.default` absolute paths with `default_import_exact` match kind when callee matches module alias.

Updated `_detect_call_expression(...)` to require `call_match_evidence.matched` instead of boolean matcher result.

Added regression test `test_detector_rejects_unbound_member_collision_for_named_import` to ensure `api.createStore(...)` does not match imported `createStore` framework path.

Verification run: `uv run --group dev basedpyright` on modified TS detector/tests (pass), `uv run ruff check` on modified files (pass), `uv run --group test pytest tests/engine/programming_language/typescript/test_typescript_additional_concept_extraction.py tests/parser/test_framework_detection_tree_sitter.py -v` (15 passed).
<!-- SECTION:NOTES:END -->
