---
id: TASK-1.1
title: >-
  Add CallExpression confidence fields to schema + ingestion docs/contracts (no
  validator integration)
status: In Progress
assignee: []
created_date: '2026-02-26 05:53'
updated_date: '2026-02-26 07:39'
labels:
  - schema
  - ingestion
  - call-expression
  - confidence
  - docs
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/backlog/docs/doc-006 -
    CallExpression-Confidence-Scoring-and-Validation-Agent.md
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_framework_definitions_ingestion.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py
documentation:
  - 'backlog://workflow/overview'
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/typescript-schema-extension-implementation-plan.md
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/prisma-call-expression-simplification-failure-cases.md
parent_task_id: TASK-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the doc-006 confidence metadata contract for ingestion-facing components only, after reviewing canonical schema, ingestion loader/tests, commons models, and framework-definition docs.

Scope
1. Add and document `base_confidence` in framework feature schema/contracts.
2. Add and document usage metadata contract for `match_confidence`, `validation_status` (`pending|completed|needs_review`), and `evidence_json`.
3. Update ingestion/commons typed models and ingestion-facing documentation to align with this contract.

Out of scope
- Validator agent implementation, trigger orchestration, or query-engine validation workflow changes.
- Mapper gating/runtime decision logic in query-engine (tracked as follow-up work).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Framework definition schema and typed contracts accept `base_confidence` for feature definitions with clear validation bounds and default behavior.
- [ ] #2 Ingestion/commons contracts define usage metadata fields `match_confidence`, `validation_status` (`pending|completed|needs_review`), and `evidence_json` with precise types and persistence compatibility.
- [ ] #3 Framework-definition documentation is updated to describe confidence fields, low-confidence guidance in feature notes, and the current non-validator scope of this task.
- [ ] #4 Ingestion loading/parsing paths preserve and normalize confidence-related feature metadata without regressing existing framework definitions.
- [ ] #5 Integration/unit tests covering schema ingestion and contract parsing are updated to assert the new fields and defaults while keeping existing behavior green.
- [ ] #6 Task artifacts explicitly state that validator agent/trigger/query-engine execution is deferred to follow-up work.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Started implementation. Reviewing canonical schema, ingestion loader/query service, commons models, relational usage model, and contributor docs for confidence-field contract alignment.

Implemented schema + ingestion contract updates for confidence metadata (validator workflow still deferred):
- Commons contracts: added `ValidationStatus` enum (`pending|completed|needs_review`), added `base_confidence` (default `0.85`, bounded `0..1`) to `FeatureSpec`/`FrameworkFeaturePayload`, and added typed `FeatureUsagePayload` (`match_confidence`, `validation_status`, `evidence_json`).
- Commons relational model: extended `UnoplatCodeConfluenceFileFrameworkFeature` with `match_confidence`, `validation_status`, and `evidence_json`.
- Ingestion loader/query/parser/persistence: normalized `base_confidence` in framework loader, resolved confidence from `feature_definition` in query service, emitted usage metadata (`match_confidence`, `validation_status='pending'`, `evidence_json`) from parser, and persisted those fields in relational ingestion upsert.
- Framework definition schema/docs: added `base_confidence` to `framework-definitions/schema.json`, updated framework definitions README guidance (including low-confidence note guidance), and synced docs schemas + contributor docs page.
- Tests: added/updated tests covering defaults and normalization paths for `base_confidence` and typed usage payloads in commons + ingestion unit/integration tests.
- Verification completed on touched scope: ruff checks passed, targeted basedpyright checks on touched ingestion source files passed, schema validation passed, and targeted commons/ingestion tests passed.

Files captured for TASK-1.1 implementation:
- unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/__init__.py
- unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/__init__.py
- unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py
- unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py
- unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py
- unoplat-code-confluence-commons/tests/test_engine_models.py
- unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
- unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md
- unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/code_confluence_codebase_parser.py
- unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py
- unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py
- unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_query_service.py
- unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/processor/db/test_framework_loader.py
- unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_framework_definitions_ingestion.py
- unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema.json
- unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v3.json
- unoplat-code-confluence-docs/content/docs/contribution/custom-framework-schema/index.mdx
- unoplat-code-confluence-query-engine/backlog/docs/doc-006 - CallExpression-Confidence-Scoring-and-Validation-Agent.md
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Schema validation and ingestion tests for touched areas pass locally.
- [ ] #2 Updated schema/docs/contracts are aligned and references in task remain accurate.
- [ ] #3 Scope boundary is preserved: no validator agent/trigger/query-engine workflow code is included.
<!-- DOD:END -->
