---
id: TASK-3.2.3
title: Implement deterministic CallExpression scoring + enriched metadata emission
status: Done
assignee: []
created_date: '2026-03-05 09:56'
updated_date: '2026-03-10 09:31'
labels:
  - confidence-scoring
  - framework-detection
  - metadata
  - call-expression
dependencies:
  - TASK-3.2.1
  - TASK-3.2.2
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/code_confluence_codebase_parser.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py
parent_task_id: TASK-3.2
priority: high
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement deterministic confidence scoring for CallExpression detections in both Python and TypeScript detectors using typed match evidence, and emit enriched metadata (`match_confidence`, match provenance keys, policy version) for each detection while leaving non-CallExpression concepts unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both detectors compute deterministic CallExpression confidence from base_confidence + match evidence with clamped [0.0, 1.0] output.
- [x] #2 CallExpression metadata includes `match_confidence`, `call_match_kind`, `matched_absolute_path`, optional `matched_alias`, and a scoring policy version marker.
- [x] #3 No fallback-specific flags are used; provenance is encoded via match_kind taxonomy.
- [x] #4 Non-CallExpression concepts keep existing metadata behavior.
- [x] #5 Parser/ingestion path continues to persist match_confidence/evidence_json without schema migrations.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented deterministic CallExpression scoring helpers in both Python and TypeScript detectors using base_confidence + match-kind adjustments + ambiguity penalties, with clamp to [0.0, 1.0].

Added enriched CallExpression metadata emission in both detectors: `match_confidence`, `call_match_kind`, `matched_absolute_path`, optional `matched_alias`, `call_confidence_policy_version` (plus existing concept/source).

Kept non-CallExpression metadata behavior unchanged (FunctionDefinition/Inheritance/AnnotationLike paths unchanged).

`_detect_call_expression(...)` now uses typed call-match evidence and metadata builder helpers in both detectors.

Parser/ingestion path remains schema-compatible and unchanged (`_resolve_match_confidence(...)` / `upsert_file_features(...)` consume metadata `match_confidence` as before).

Verification: targeted basedpyright + ruff on modified detector/test files passed; targeted detector pytest suites passed (15 tests).
<!-- SECTION:NOTES:END -->
