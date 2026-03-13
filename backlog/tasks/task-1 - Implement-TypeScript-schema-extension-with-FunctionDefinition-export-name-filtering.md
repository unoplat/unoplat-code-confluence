---
id: TASK-1
title: >-
  Implement TypeScript schema extension with FunctionDefinition + export-name
  filtering
status: Done
assignee: []
created_date: '2026-02-25 06:16'
updated_date: '2026-03-10 09:31'
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
  - 'https://nextjs.org/docs/app/building-your-application/routing/route-handlers'
  - 'https://nextjs.org/docs/app/api-reference/file-conventions/route'
  - 'https://tree-sitter.github.io/py-tree-sitter/classes/tree_sitter.Query.html'
  - >-
    https://tree-sitter.github.io/py-tree-sitter/classes/tree_sitter.QueryCursor.html
priority: high
ordinal: 7000
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
- [ ] #7 TypeScript language pipeline wires framework detection service so `.ts` files can emit `custom_features_list` detections for Next.js route handlers.
- [ ] #8 Import-gated matching is enforced for TypeScript: exported HTTP handlers are only matched when `next/server` absolute-path imports are present.
- [ ] #9 A canonical `framework-definitions/typescript/nextjs.json` definition is added and passes schema validation with existing v3 schema.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Objective
Implement end-to-end TypeScript framework detection for Next.js route handlers by reusing the existing schema/DB contracts and mirroring the Python detection pipeline architecture.

Scope Boundary
- In scope: TypeScript `FunctionDefinition` detection for Next.js App Router route handlers in `.ts` files (e.g., `route.ts` exports like `GET`, `POST`).
- Out of scope: validator-agent workflow integration (covered by TASK-1.2), TSX-specific route detection, additional TypeScript concepts beyond `FunctionDefinition`.

Phase 1 - Framework Definition Catalog (ingestion input)
1) Create `framework-definitions/typescript/nextjs.json`.
2) Add library `nextjs` with feature `route_handler_export`:
   - `concept`: `FunctionDefinition`
   - `target_level`: `function`
   - `startpoint`: `true`
   - `construct_query.function_name_regex`: `^(GET|HEAD|POST|PUT|DELETE|PATCH|OPTIONS)$`
   - `construct_query.export_name_regex`: `^(GET|HEAD|POST|PUT|DELETE|PATCH|OPTIONS)$`
   - `absolute_paths`: import gates from `next/server` symbols (initially `next/server.NextRequest`, `next/server.NextResponse`)
   - `base_confidence`: set explicitly for deterministic downstream confidence seeding.
3) Keep schema unchanged unless validation reveals a gap; current v3 contract already includes needed fields.

Phase 2 - TypeScript Source Context + Import Alias Model
Algorithm (deterministic import extraction)
1) Parse TypeScript source once using tree-sitter; keep a shared context object (`source_bytes`, `tree`, `root_node`).
2) Walk `import_statement` nodes and extract:
   - module source string (e.g., `next/server`)
   - default import alias (`import x from 'm'` -> `m -> x`)
   - namespace alias (`import * as ns from 'm'` -> `m -> ns`)
   - named imports (`import { A, B as C } from 'm'` -> `m.A -> A`, `m.B -> C`)
   - type-only named imports handled same as named imports for import gating.
3) Build `import_aliases: dict[str, str]` in canonical form compatible with DB `absolute_paths` (e.g., `next/server.NextResponse -> NextResponse`, `next/server -> nextServer`).
4) Deduplicate + preserve deterministic ordering for reproducible downstream matching/debug logs.

Phase 3 - TypeScript Query Builder (`FunctionDefinition`)
Algorithm (query generation)
1) Add a TypeScript query template for exported function declarations:
   - capture export statement (`@export_statement`)
   - capture declaration node (`@function_definition`)
   - capture function name (`@function_name`)
   - capture export name (`@export_name`)
2) Render predicates from `construct_query`:
   - apply `#match? @function_name ...` when `function_name_regex` is present
   - apply `#match? @export_name ...` when `export_name_regex` is present
3) Cache compiled query by hash(feature definition payload) for performance parity with Python.

Phase 4 - TypeScript Tree-Sitter Framework Detector
Algorithm (feature matching)
1) For each `FeatureSpec`, enforce import gating first:
   - match if any `absolute_path` exists directly in `import_aliases`
   - or module prefix strategy matches (symbol imported via module alias path).
2) Concept dispatch:
   - implement `Concept.FUNCTION_DEFINITION`
   - explicitly skip unsupported concepts for TypeScript detector with debug logging.
3) Execute query and create detections from `@function_definition` spans:
   - `start_line`, `end_line`, `match_text`
   - metadata: `concept='FunctionDefinition'`, `source='tree_sitter'`, `match_confidence=feature_spec.base_confidence`.
4) Deduplicate identical span+feature rows in-memory before return.

Phase 5 - TypeScript Framework Detection Service (DB-backed)
Algorithm (service orchestration)
1) Guard language == `typescript`; return empty otherwise.
2) Build TypeScript source context.
3) Expand import paths for DB lookup (module path and hierarchical prefixes where applicable).
4) Query PostgreSQL using existing `get_framework_features_for_imports(session, 'typescript', imports)`.
5) Pass `FeatureSpec` set to TypeScript detector and return detections.
6) Error handling/logging should mirror Python service behavior.

Phase 6 - Parser/Processor Wiring
1) `CodeConfluenceCodebaseParser`:
   - instantiate TypeScript framework detection service when codebase language is TypeScript.
2) `TypeScriptLanguageProcessor`:
   - extract imports (no longer `imports=None`)
   - call injected framework detection service
   - populate `custom_features_list` with detections
   - keep existing data-model detection behavior intact.

Phase 7 - Tests (unit + integration)
1) Definition/loader tests:
   - ensure `framework-definitions/typescript/nextjs.json` is loaded and preserves `FunctionDefinition` regex config.
2) Source-context tests:
   - validate alias extraction for default/named/aliased/namespace/type imports from `next/server`.
3) Detector tests:
   - positive: detects `export async function GET(...)` when `next/server` import exists
   - negative: no detection without import gate
   - regex filter: `GET` matches; non-HTTP export does not
   - alias variant (`NextResponse as Resp`) still satisfies import gate.
4) Processor tests:
   - TypeScript processor returns `imports` and `custom_features_list` for Next.js route sample.
5) Optional Postgres integration:
   - DB-seeded TypeScript definitions produce detections via service path.

Phase 8 - Validation + Quality Gates
Execution order
1) `uv run --group dev basedpyright src/`
2) `uv run ruff check src/`
3) `uv run --group dev check-jsonschema --schemafile framework-definitions/schema.json framework-definitions/*/*.json`
4) `uv run --group test pytest` for targeted TypeScript framework-detection tests, then broader suite if needed.

Key Risks + Mitigations
- Risk: import alias edge cases in TypeScript grammar (type-only imports, aliases).
  Mitigation: dedicated source-context tests for each import form.
- Risk: false positives on exported helper functions.
  Mitigation: strict HTTP-method regex + import gating on `next/server` symbols.
- Risk: regression in existing TypeScript processor assumptions (`imports=None`).
  Mitigation: update processor tests and keep backward-compatible optional imports field in `UnoplatFile`.

Handoff Notes
- Keep validator/agent-trigger logic untouched in this task.
- If additional concepts are requested during implementation, pause and route as explicit scope change against TASK-1 acceptance criteria.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Set TASK-1 status to In Progress and prepared a concrete implementation sequence aligned with the TypeScript schema extension plan.

Implemented contract changes, schema updates, loader scanning updates, docs updates, and focused tests across flow-bridge, commons, and query-engine.

Validation executed: check-jsonschema (framework-definitions/*/*.json), flow-bridge targeted pytest + ruff + basedpyright, commons targeted pytest, query-engine targeted pytest, and compileall checks.

Detailed implementation flow was expanded on 2026-02-28 after repository audit. Key finding: schema/contracts already support `FunctionDefinition`; primary gap is missing TypeScript runtime pipeline (source-context/query-builder/detector/service wiring) and missing TypeScript framework definitions catalog file.

Design decision: mirror Python detector architecture for parity and maintainability, but restrict TypeScript detector scope in this task to `FunctionDefinition` route handlers for Next.js App Router.

Design decision: preserve confidence contract from TASK-1.1 by stamping `match_confidence` from `FeatureSpec.base_confidence` into detection metadata, allowing downstream validator flow in TASK-1.2 to remain unchanged.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Unit/integration tests added or updated for schema parsing + matching behavior.
- [ ] #2 No regressions for existing framework definitions that use `CallExpression`/`AnnotationLike`/`Inheritance`.
<!-- DOD:END -->
