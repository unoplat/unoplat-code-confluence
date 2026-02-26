---
id: TASK-1
title: >-
  Implement TypeScript schema extension with FunctionDefinition + export-name
  filtering
status: In Progress
assignee: []
created_date: '2026-02-25 06:16'
updated_date: '2026-02-25 11:49'
labels:
  - typescript
  - schema
  - ingestion
  - query-engine
  - validator
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/typescript-schema-extension-implementation-plan.md
  - >-
    unoplat-code-confluence-query-engine/backlog/docs/doc-006 -
    CallExpression-Confidence-Scoring-and-Validation-Agent.md
documentation:
  - 'backlog://workflow/overview'
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the TypeScript schema extension from `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/typescript-schema-extension-implementation-plan.md` using the simplified concept strategy.

Scope
1. Add only `FunctionDefinition` to concept coverage for TypeScript extension.
2. Add `construct_query.function_name_regex` and `construct_query.export_name_regex`.
3. Reuse existing concepts (`AnnotationLike`, `CallExpression`, `Inheritance`) and avoid adding new concept enums that are no longer needed.
4. Keep `CallExpression` matching heuristic and rely on validator flow for low-confidence cases (per backlog doc-006).

Out of scope
- Backward compatibility toggles for disabling validator.
- New TypeScript concepts beyond the agreed minimal set.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Framework schema accepts and validates `FunctionDefinition` for TypeScript extension rules.
- [ ] #2 `construct_query.export_name_regex` and `construct_query.function_name_regex` are implemented and covered by tests.
- [ ] #3 Next.js route-handler style exports (e.g., `export async function GET`) are matchable via `FunctionDefinition` + export-name regex.
- [ ] #4 Prisma-style call expression detection remains based on absolute imports + `CallExpression`, with validator handoff for ambiguous cases.
- [ ] #5 No additional TypeScript concept enums are introduced beyond `FunctionDefinition` in this change.
- [ ] #6 Implementation docs and examples remain aligned with the updated plan and validator assumptions.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update shared contracts in commons and query-engine for FunctionDefinition and new construct_query regex keys.
2. Extend canonical and public schema mirrors with FunctionDefinition and function/export regex fields.
3. Relax absolute_paths schema pattern for TypeScript package/module forms while preserving terminal symbol requirement.
4. Update flow-bridge loader to discover framework definition files across all language directories.
5. Keep payload normalization compatible with FunctionDefinition values during ingestion.
6. Update validation workflow commands and framework-definition contributor docs.
7. Add targeted unit tests in commons/query-engine and loader-focused tests in flow-bridge.
8. Run targeted schema validation, lint/type checks, and pytest suites.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Set TASK-1 status to In Progress and prepared a concrete implementation sequence aligned with the TypeScript schema extension plan.

Implemented contract changes, schema updates, loader scanning updates, docs updates, and focused tests across flow-bridge, commons, and query-engine.

Validation executed: check-jsonschema (framework-definitions/*/*.json), flow-bridge targeted pytest + ruff + basedpyright, commons targeted pytest, query-engine targeted pytest, and compileall checks.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Unit/integration tests added or updated for schema parsing + matching behavior.
- [ ] #2 No regressions for existing framework definitions that use `CallExpression`/`AnnotationLike`/`Inheritance`.
<!-- DOD:END -->
