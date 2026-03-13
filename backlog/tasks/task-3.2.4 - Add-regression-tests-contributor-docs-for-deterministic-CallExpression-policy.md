---
id: TASK-3.2.4
title: >-
  Add regression tests + contributor docs for deterministic CallExpression
  policy
status: Done
assignee: []
created_date: '2026-03-05 09:56'
updated_date: '2026-03-10 09:31'
labels:
  - testing
  - documentation
  - framework-definitions
  - call-expression
dependencies:
  - TASK-3.2.3
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/test_framework_detection_tree_sitter.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/engine/programming_language/typescript/test_typescript_additional_concept_extraction.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md
parent_task_id: TASK-3.2
priority: high
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add/update detector and integration tests validating import-bound CallExpression matching semantics and deterministic confidence behavior, then document contributor guidance for scoring/evidence fields and no-suffix-fallback policy in framework-definition docs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Python and TypeScript tests cover positive import-bound matches and negative ambiguous-collision non-matches for CallExpression.
- [x] #2 Any touched loader/parser tests pass with deterministic confidence metadata assertions.
- [x] #3 README explicitly documents CallExpression import-bound matching semantics, evidence fields, and deterministic confidence policy expectations.
- [x] #4 Verification sequence succeeds in order: typecheck, lint, targeted tests for touched suites.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Expanded detector regression coverage for CallExpression semantics in Python/TypeScript tests, including negative ambiguous-collision non-match case (`api.createStore(...)`).

Added metadata assertions in detector tests for deterministic CallExpression evidence fields (`match_confidence`, `call_match_kind`, `matched_absolute_path`, `matched_alias`, `call_confidence_policy_version`).

Updated contributor guidance in `framework-definitions/README.md` to document import-bound CallExpression matching (no suffix/member fallback), deterministic evidence metadata fields, and low-confidence notes expectations.

Verification sequence executed and passed on touched files/suites: basedpyright -> ruff check -> targeted pytest (15 passed).
<!-- SECTION:NOTES:END -->
