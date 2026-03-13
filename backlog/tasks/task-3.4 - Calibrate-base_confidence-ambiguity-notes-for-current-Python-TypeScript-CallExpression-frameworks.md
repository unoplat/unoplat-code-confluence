---
id: TASK-3.4
title: >-
  Calibrate base_confidence + ambiguity notes for current Python/TypeScript
  CallExpression frameworks
status: In Progress
assignee: []
created_date: '2026-03-04 10:56'
updated_date: '2026-03-10 09:32'
labels:
  - framework-definitions
  - confidence-scoring
  - python
  - typescript
  - documentation
dependencies:
  - TASK-3.6.2
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/fastapi.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/sqlmodel.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/celery.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/litellm.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/zustand.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/swr.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_framework_definitions_ingestion.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/processor/db/test_framework_loader.py
documentation:
  - >-
    unoplat-code-confluence-query-engine/backlog/docs/doc-006 -
    CallExpression-Confidence-Scoring-and-Validation-Agent.md
parent_task_id: TASK-3
priority: high
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Calibrate explicit contributor-authored `base_confidence` values and ambiguity notes for current Python/TypeScript CallExpression framework definitions after detector-side automated scoring removal. This task sets intentional manual confidence per shipped CallExpression feature and adds validator guidance notes for low-confidence entries so query-engine gating reflects contributor intent rather than arithmetic heuristics. Under current query-engine threshold semantics, only `base_confidence < 0.70` routes to validator.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every currently shipped Python CallExpression feature definition has an explicit contributor-authored base_confidence value (no implicit default reliance).
- [ ] #2 Every currently shipped TypeScript CallExpression feature definition has an explicit contributor-authored base_confidence value.
- [ ] #3 CallExpression definitions that should route to validator use `base_confidence < 0.70` and include actionable disambiguation notes for validator review.
- [ ] #4 High-confidence CallExpression definitions document rationale via notes or surrounding docs where needed.
- [ ] #5 Schema validation succeeds for all modified framework definition files.
- [ ] #6 Framework loader/integration tests asserting CallExpression base_confidence handling pass after calibration.
- [ ] #7 README guidance clearly documents manual CallExpression confidence calibration principles and that current validator pickup uses `< 0.70`.
- [ ] #8 Flow-bridge typecheck then lint then targeted framework-definition tests pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1) Inventory all currently shipped CallExpression features and make confidence explicit.
- Python files: `fastapi.json`, `sqlmodel.json`, `celery.json`, `litellm.json`.
- TypeScript files: `zustand.json`, `swr.json` (and any additional current TS CallExpression definitions).
- Add explicit `base_confidence` to every CallExpression feature currently relying on schema default.

2) Calibrate confidence by ambiguity class.
- High precision direct API symbols with low collision risk -> high values (~0.85-0.95).
- Moderate collision APIs -> medium values (~0.70-0.84).
- High-collision or provenance-sensitive APIs -> below validator threshold (<0.70) with clear notes.

3) Add disambiguation notes for low-confidence features.
- For any feature set below threshold, add `notes` that tell validator what to confirm (import binding, object provenance, API shape, expected args/usage context).
- Ensure notes are concrete and framework-specific (not generic text).

4) Update contributor documentation.
- Extend `framework-definitions/README.md` with explicit manual-confidence guidance for CallExpression and examples of when to set low confidence + mandatory notes.
- Clarify that official docs links are necessary but not sufficient for ambiguous low-confidence features; notes should provide disambiguation checks for validator execution.

5) Validate definitions and loader behavior.
- Run schema validation and framework loader/integration tests that assert confidence normalization and parsing.
- Ensure modified JSON files pass schema and ingestion tests without broad unrelated changes.

6) Verification.
- Run flow-bridge checks in order: typecheck -> lint -> targeted tests for framework loader/integration + relevant detector tests.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added explicit manual `base_confidence` values to shipped CallExpression definitions: FastAPI background tasks (0.88), SQLModel relationship (0.86), Celery schedule expressions (0.69), LiteLLM completion/embedding (0.69), Zustand store/immer helpers (0.69), SWR hooks (0.91).

Added actionable validator notes for low-confidence entries that should route under current `< 0.70` threshold semantics (Celery, LiteLLM, Zustand).

Updated README and docs/public framework-definition mirrors to reflect CallExpression-only confidence semantics and current validator threshold behavior.

Verification so far: modified flow-bridge unit tests passed; targeted integration tests blocked by local Docker port 5432 already in use.
<!-- SECTION:NOTES:END -->
