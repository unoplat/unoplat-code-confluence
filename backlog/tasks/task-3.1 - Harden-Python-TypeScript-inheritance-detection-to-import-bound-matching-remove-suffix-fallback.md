---
id: TASK-3.1
title: >-
  Harden Python/TypeScript inheritance detection to import-bound matching
  (remove suffix fallback)
status: Done
assignee: []
created_date: '2026-03-03 11:59'
updated_date: '2026-03-03 13:04'
labels:
  - bugfix
  - framework-detection
  - python
  - typescript
  - tree-sitter
  - detection-accuracy
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_source_context.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_source_context.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md
parent_task_id: TASK-3
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context
Current inheritance matching in both Python and TypeScript detectors accepts suffix-based matches (e.g., `foo.BaseModel`, `foo.LitElement`) when any related framework import exists in the file. This produces false-positive framework detections and pollutes downstream app-interface mapping.

## Problem Statement
- Python and TypeScript inheritance detection currently treat `*.ShortName` as a match.
- This allows unrelated objects to match framework base classes.
- The matcher is not strictly bound to imported symbols/aliases.

## Goal
Make inheritance detection deterministic by requiring import-bound superclass matches only, and remove suffix fallback logic for inheritance in both languages.

## In Scope
- Python inheritance matcher hardening
- TypeScript inheritance matcher hardening
- Positive/negative regression tests for both languages
- Documentation update in framework-definitions README to state inheritance matching is import-bound and suffix fallback is not used

## Out of Scope (separate follow-up)
- CallExpression matcher hardening
- Cross-language validator workflow expansion
- Schema-level mandatory `superclass_regex` requirements

## Proposed Behavior
For each inheritance feature absolute path (e.g., `pydantic.BaseModel`, `lit.LitElement`), accepted superclass forms must resolve from file imports:
- Direct symbol import alias (e.g., `BaseModel`, `BM`)
- Module import alias + symbol (e.g., `pd.BaseModel`)
- Exact known non-aliased module + symbol where applicable

Rejected examples:
- `foo.BaseModel` (unless `foo` is actual import alias to `pydantic`)
- `foo.LitElement` (unless `foo` is actual import alias to `lit`)

## Risk
Potential recall reduction for edge import forms currently not represented in import alias extraction. Must be covered with explicit tests and follow-up improvements where needed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Python inheritance matching no longer uses suffix fallback (`endswith('.<short_name>')`) and only accepts import-bound superclass matches.
- [x] #2 TypeScript inheritance matching no longer uses suffix fallback (`endswith('.<short_name>')`) and only accepts import-bound superclass matches.
- [x] #3 Negative regression: `from pydantic import BaseModel; class X(foo.BaseModel): ...` does not produce a pydantic inheritance detection.
- [x] #4 Negative regression: `import { LitElement } from 'lit'; class X extends foo.LitElement {}` does not produce a lit inheritance detection.
- [x] #5 Positive regression: valid alias-bound inheritance still matches (e.g., `from pydantic import BaseModel as BM; class X(BM): ...` and TS module alias form where supported by import alias extraction).
- [x] #6 Framework detection test suite for touched areas passes.
- [x] #7 Type check and lint pass after changes (typecheck first, lint second).
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1) Python detector hardening
- Update inheritance matcher in `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py` to remove suffix fallback logic.
- Build accepted superclass candidates strictly from `absolute_paths` and `context.import_aliases` (direct symbol alias + module alias member form).
- Keep behavior deterministic: no raw `*.short_name` acceptance when object prefix is not import-bound.

2) TypeScript detector hardening
- Update inheritance matcher in `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py` to remove suffix fallback logic.
- Use import-derived aliases from `TypeScriptSourceContext.import_aliases` for accepted forms.
- Ensure `foo.Symbol` only matches when `foo` resolves to imported module alias for a declared absolute path.

3) Tests (required)
- Add/update Python detector tests with one negative repro (`foo.BaseModel`) and one positive alias-bound case (`BaseModel as BM`).
- Add/update TypeScript detector tests with one negative repro (`foo.LitElement`) and one positive import-bound case.
- Keep tests minimal and concept-focused (inheritance only in this task).

4) Documentation sync for behavior semantics
- Update `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md` to state inheritance detection uses import-bound matching and no suffix fallback.

5) Validation run order (project convention)
- In flow-bridge: run typecheck first, then lint, then targeted tests for modified detector/tests.
- Commands should use uv (and `--group test` for pytest).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created to isolate deterministic inheritance-matching hardening from broader call-expression/validator work.

Follow-up task will address call-expression confidence policy + validator expansion across languages.

2026-03-03: Started implementation. First pass focuses on inheritance matcher hardening (import-bound only) across Python and TypeScript, removing suffix fallback in both detectors before confidence-policy/validator follow-up tasks.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed suffix-based superclass matching in both inheritance detectors and made matches import-bound only.

Added regression coverage for Python (`foo.BaseModel` reject, `BaseModel as BM` accept) and TypeScript (`foo.LitElement` reject, `LitElement as BaseElement` accept).

Updated framework-definitions README to document import-bound inheritance semantics and no suffix fallback.

Validation: targeted basedpyright on modified detector files passed; ruff check on modified files passed; targeted pytest for updated detector suites passed (12 tests).

Project-wide `task typecheck` still reports pre-existing unrelated errors outside touched files (baseline).
<!-- SECTION:FINAL_SUMMARY:END -->
