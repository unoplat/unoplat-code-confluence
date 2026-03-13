---
id: TASK-3.6
title: >-
  Replace detector-scored CallExpression confidence with contributor-authored
  manual confidence
status: Done
assignee: []
created_date: '2026-03-06 05:58'
updated_date: '2026-03-10 09:32'
labels:
  - framework-detection
  - call-expression
  - confidence-scoring
  - schema
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md
parent_task_id: TASK-3
priority: high
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace detector-scored CallExpression confidence with contributor-authored manual confidence, and scope confidence semantics to CallExpression only. The current deterministic score adjustments are based only on file-local import binding and callee shape, which is insufficient for SDK instance provenance, wrapper factories, and cross-file client usage. Preserve deterministic import-bound match evidence and existing validator plumbing, but make confidence an explicit CallExpression-only concept authored in framework definitions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Detector-side automated CallExpression confidence arithmetic is removed for Python and TypeScript while import-bound match evidence remains intact.
- [ ] #2 CallExpression `match_confidence` is sourced directly from contributor-authored `base_confidence`, not computed bonuses/penalties.
- [ ] #3 Confidence configuration is scoped to CallExpression only; non-CallExpression concepts do not define or emit `base_confidence` / `match_confidence` as part of this rollout.
- [ ] #4 Schema/loader/parsers require explicit `base_confidence` for CallExpression definitions without broadening the requirement to other concepts.
- [ ] #5 Existing framework-definition CallExpression entries are updated to explicit manual confidence values, using `< 0.70` for entries that should route to validator under current query-engine threshold semantics.
- [ ] #6 Docs/tests reflect CallExpression-only manual-confidence policy and targeted validation/typecheck/lint/test commands pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1) Roll back detector-side automated CallExpression score adjustments while preserving import-bound evidence.
- Remove runtime bonus/penalty arithmetic from Python and TypeScript CallExpression detector metadata builders.
- Keep `call_match_kind`, `matched_absolute_path`, optional `matched_alias`, and current import-bound/no-suffix-fallback matching semantics.
- Keep `match_confidence` populated for CallExpression only, sourced directly from contributor-authored `spec.base_confidence`.

2) Enforce confidence as a CallExpression-only concern.
- Update schema and typed models so `base_confidence` is valid only for `concept=CallExpression`.
- Remove non-CallExpression confidence defaults/emission from parsers/detectors touched by this flow.
- Preserve non-CallExpression detection behavior otherwise.

3) Enforce manual confidence at the definition layer for CallExpression only.
- Update schema conditional rules so `concept=CallExpression` requires explicit `base_confidence`.
- Preserve low-confidence notes requirement for `< 0.70` CallExpression entries.
- Remove CallExpression-only silent fallback/defaulting in loader for missing/invalid confidence.

4) Calibrate shipped CallExpression definitions.
- Add explicit `base_confidence` to current Python/TypeScript CallExpression framework definitions.
- Use values `< 0.70` for entries that should route to validator under current query-engine gating.
- Add actionable `notes` to low-confidence entries.

5) Align tests and docs.
- Update detector/tests to assert CallExpression-only confidence behavior and evidence fields.
- Update schema/loader tests for explicit CallExpression confidence enforcement.
- Revise README guidance to note validator pickup is triggered by `< 0.70` under current query-engine behavior.

6) Verify end-to-end touched scope.
- Run typecheck -> lint -> targeted pytest for commons, detectors, schema/loader, and framework-definition validation suites.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-03-06: Re-scoped CallExpression confidence work away from detector-side arithmetic. New direction: preserve import-bound evidence, but make CallExpression confidence contributor-authored via explicit schema `base_confidence` only.

Implemented CallExpression-only confidence semantics across detectors/schema/loader/query-service paths. Non-CallExpression detector metadata no longer emits `match_confidence`; FunctionDefinition Next.js definitions/tests were updated accordingly.

Current validator threshold semantics confirmed from query-engine repository code: only rows with `match_confidence < 0.70` become validator candidates; `0.70` itself bypasses validator unless query-engine threshold logic is changed.
<!-- SECTION:NOTES:END -->
