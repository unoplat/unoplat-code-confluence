---
id: TASK-3.6.2
title: Enforce explicit manual CallExpression base_confidence in schema and loader
status: Done
assignee: []
created_date: '2026-03-06 06:01'
updated_date: '2026-03-10 09:31'
labels:
  - schema
  - framework-definitions
  - call-expression
  - loader
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py
parent_task_id: TASK-3.6
priority: high
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enforce contributor-authored `base_confidence` for CallExpression definitions only by tightening schema and loader behavior without changing unrelated concept semantics. Confidence should exist only for CallExpression in this rollout, and low-confidence validator routing follows current query-engine threshold semantics where only values `< 0.70` are selected.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Schema requires explicit `base_confidence` when `concept = CallExpression` and keeps non-CallExpression concepts unchanged.
- [x] #2 Low-confidence CallExpression definitions still require actionable `notes` when `base_confidence < 0.70`.
- [x] #3 Loader no longer silently defaults missing/invalid CallExpression `base_confidence` values to `0.85`, and non-CallExpression payloads do not retain `base_confidence`.
- [x] #4 Validation tests cover missing/invalid CallExpression `base_confidence` handling and non-CallExpression rejection of confidence fields.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated schema/loader path so `base_confidence` is a CallExpression-only field: schema requires it for `concept=CallExpression`, requires `notes` when `base_confidence < 0.70`, and forbids it on other concepts.

Loader/query service now enforce explicit numeric CallExpression confidence and strip/omit non-CallExpression confidence from parsed feature definitions/specs.

Updated docs/public schema mirrors plus framework definitions so shipped CallExpression entries now use explicit manual confidence values, with ambiguous entries set to `< 0.70` for validator routing under current query-engine semantics.

Verification: flow-bridge basedpyright on modified source/unit-test files passed; flow-bridge ruff passed; modified loader/unit detector tests passed. Targeted integration tests were blocked by local Docker port 5432 conflict before test logic executed.
<!-- SECTION:NOTES:END -->
