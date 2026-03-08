---
id: TASK-3.2
title: >-
  Implement deterministic CallExpression confidence policy for Python +
  TypeScript detectors
status: Done
assignee: []
created_date: '2026-03-04 10:56'
updated_date: '2026-03-05 10:27'
labels:
  - framework-detection
  - confidence-scoring
  - python
  - typescript
  - call-expression
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/code_confluence_codebase_parser.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/test_framework_detection_tree_sitter.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/engine/programming_language/typescript/test_typescript_additional_concept_extraction.py
documentation:
  - >-
    unoplat-code-confluence-query-engine/backlog/docs/doc-006 -
    CallExpression-Confidence-Scoring-and-Validation-Agent.md
parent_task_id: TASK-3
priority: high
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context
CallExpression detections currently rely mostly on base confidence defaults and coarse import/callee heuristics. This causes high-confidence false positives (especially short-name collisions like `api.create`) and prevents low-confidence validator gating from activating consistently.

## Goal
Introduce deterministic, explainable confidence scoring for every CallExpression match in Python and TypeScript detection paths, with rich evidence persisted in metadata so downstream validation can reliably select low-confidence candidates.

## Scope
- Python tree-sitter detector call-expression matching and metadata
- TypeScript tree-sitter detector call-expression matching and metadata
- Parser/ingestion confidence propagation verification
- Unit tests for positive/negative scoring behavior

## Out of Scope
- Temporal validator workflow expansion (covered in separate task)
- New framework definitions (covered separately)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every Python CallExpression detection writes metadata.match_confidence in [0.0, 1.0] using deterministic policy logic (no implicit default-only behavior).
- [x] #2 Every TypeScript CallExpression detection writes metadata.match_confidence in [0.0, 1.0] using deterministic policy logic.
- [x] #3 Call-expression matcher returns structured match evidence with import-bound exact kinds (for example: symbol_exact, import_alias_exact, module_member_exact, default_import_exact), and scoring uses that evidence.
- [x] #4 Python and TypeScript `_matches_callee(...)` do not use suffix/member fallback heuristics (`endswith(...)`) for framework-call matching.
- [x] #5 Known ambiguous collision scenario (for example: imported `createStore` plus unrelated `api.createStore(...)`) does not produce a framework detection unless the object/module qualifier is import-bound to the framework symbol path.
- [x] #6 Non-CallExpression concepts are unaffected by this change.
- [x] #7 Parser ingestion persists scored match_confidence values into `code_confluence_file_framework_feature` rows via existing pipeline.
- [x] #8 Python and TypeScript detector tests include both high-confidence positive and ambiguous-collision negative cases and pass.
- [x] #9 Flow-bridge typecheck then lint then targeted tests pass for touched files/suites.
- [x] #10 Scoring policy and evidence fields are documented in framework-definitions README (or equivalent detector docs) for contributor consistency, including import-bound call matching and no suffix fallback semantics.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1) Add structured CallExpression match evidence in both detectors.
- Introduce a typed match-evidence shape (module-level helper + TypedDict/dataclass) with: matched(bool), match_kind(str literal), matched_absolute_path(str), matched_alias(str|None).
- Restrict match_kind taxonomy to import-bound exact outcomes (plus no_match) rather than suffix/member fallback categories.
- Update Python `_matches_callee(...)` to return evidence instead of bool and preserve intended import-bound matching behavior.
- Update TypeScript `_matches_callee(...)` similarly, including default-import path handling (`*.default`).

2) Remove suffix/member fallback heuristics from CallExpression matching.
- Eliminate `endswith(...)`-style suffix/member fallback acceptance in Python and TypeScript call matchers.
- Ensure calls only match when symbol/module binding is backed by import alias resolution.

3) Add deterministic scoring helper used only for CallExpression.
- Add module-level scoring helper in each detector (no nested functions) that computes deterministic confidence from base_confidence + evidence-kind adjustments and clamps to [0.0, 1.0].
- Keep policy reproducible: same inputs (feature + callee + import aliases + match_kind) must always produce the same confidence.

4) Emit enriched metadata for every CallExpression detection.
- Python and TypeScript `CallExpressionInfo.metadata` must include at minimum:
  `concept`, `source`, `match_confidence`, `call_match_kind`, `matched_absolute_path`, optional `matched_alias`, and a policy version key (for auditability).
- Keep non-CallExpression metadata unchanged.

5) Verify parser/ingestion propagation path with no schema changes.
- Reuse existing `_resolve_match_confidence(...)` in parser and `upsert_file_features(...)` persistence path.
- Add/adjust tests where needed to confirm scored confidence propagates to DB rows.

6) Add regression tests for confidence behavior.
- Python detector tests: one exact import-bound call (high confidence) + one unrelated member-call collision case (no detection / negative assertion).
- TypeScript detector tests: include known false-positive pattern (`import { createStore } ...` with unrelated `api.createStore(...)`) and assert non-match.
- Ensure no behavior regressions for inheritance/annotation/function-definition tests.

7) Documentation + verification.
- Update `framework-definitions/README.md` with scoring/evidence semantics and explicit no-suffix-fallback guidance for CallExpression matching.
- Run validation in order: flow-bridge typecheck -> lint -> targeted pytest for touched suites.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-03-05: Broke implementation into child tasks: TASK-3.2.1 (TypeScript matcher evidence/import-bound), TASK-3.2.2 (Python matcher evidence/import-bound), TASK-3.2.3 (deterministic scoring + metadata emission), TASK-3.2.4 (tests + docs + verification).

Execution order: 3.2.2 -> 3.2.1 -> 3.2.3 -> 3.2.4.

2026-03-05: Completed implementation via subtasks TASK-3.2.2 (Python matcher evidence/import-bound), TASK-3.2.1 (TypeScript matcher evidence/import-bound), TASK-3.2.3 (deterministic scoring + metadata), TASK-3.2.4 (tests + docs).

Detectors now use typed CallExpression match evidence, import-bound matching semantics (no suffix/member fallback), and deterministic confidence scoring with auditable metadata fields.

Regression coverage includes positive import-bound matches and negative collision non-matches across Python and TypeScript.

Verification executed in sequence on touched files: basedpyright -> ruff check -> targeted pytest (15 passed).
<!-- SECTION:NOTES:END -->
