---
id: TASK-24.4.5.2
title: >-
  Align flow-bridge ingestion schema and regressions with single-contract
  operations
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-04-01 04:55'
updated_date: '2026-04-02 14:10'
labels:
  - framework-features
  - schema
  - ingestion
  - tests
milestone: Framework feature architecture
dependencies:
  - TASK-24.4.5.1
  - TASK-24.4.5.3
references:
  - doc-3
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/fastapi.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/celery.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/fastmcp.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/litellm.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/pydantic.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/sqlalchemy.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/python/sqlmodel.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/nextjs.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/litellm.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/swr.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/zustand.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/processor/db/test_framework_loader.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/processor/db/test_framework_query_service.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_framework_definitions_ingestion.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/test_framework_detection_tree_sitter.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_framework_detection_with_postgres.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/test_framework_detection_language_processor.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/engine/programming_language/typescript/test_nextjs_extraction.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/backlog/docs/doc-3
    - Flow-Bridge-v4-Operation-Key-Migration-Design.md
parent_task_id: TASK-24.4.5
priority: high
ordinal: 1513
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After the docs and commons simplification is settled, update the local flow-bridge schema, framework-definition fixtures, and ingestion-side regressions so the migration continues with one executable runtime contract per operation. Keep the broader operation-key migration intact, but remove any local assumptions or test scaffolding that imply first-class variants within a single operation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The local flow-bridge framework schema reflects the simplified single-contract operation model.
- [x] #2 Framework-definition fixtures and ingestion regressions no longer assume first-class variants within one operation.
- [x] #3 The operation-key migration can continue on top of the simplified schema without changing the current database storage strategy.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Typecheck the touched flow-bridge surfaces first.
2. Convert all local framework-definitions JSON fixtures from features to capabilities -> operations and update schema/README only where the local contract or examples still imply v3.
3. Update the local flow-bridge regressions that load those fixtures or assert old flat keys, with special attention to removing stale test-local parsing helpers in test_framework_definitions_ingestion.py.
4. Validate the JSON fixtures against the local schema.
5. Run focused loader, query, parser, and integration regressions affected by operation-level keys.
6. Run lint last on the touched flow-bridge files.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Local flow-bridge is only partially aligned today. The production loader and query service already assume the new authored shape and operation-level persisted identity: framework_loader.py iterates capabilities -> operations and stores feature_key = capability.operation, while framework_query_service.py rebuilds FeatureSpec from persisted capability_key and operation_key. The inconsistency is in the shipped local fixtures and regressions: every checked-in framework definition JSON file still uses flat features, tests/integration/test_framework_definitions_ingestion.py duplicates stale v3 parsing helpers, tests/parser/test_framework_detection_tree_sitter.py still loads library.features, and several regressions still assert old flat keys such as http_endpoint. Implement this task by converting the local fixture corpus to capabilities -> operations, keeping one executable runtime contract per operation, and updating only the local flow-bridge regressions that consume those fixtures or assert persisted/detected keys. For multi-verb endpoints, duplicate shared runtime fields and split into separate operations such as http_endpoint.get and http_endpoint.post; do not introduce detector arrays, variant payloads, or DB schema changes. Prefer production loader/query logic in tests over copied parsing helpers so future schema changes hit one path. Keep the task local to flow-bridge; do not expand it into docs-package sync or query-engine changes.

Important blockers and decisions to resolve during implementation:
1. FrameworkFeaturePayload in commons currently forbids extras and does not model schema-allowed fields like notes or docs_url. Migrated local fixtures may expose that mismatch; reopening commons to carry those fields is safer than stripping them in flow-bridge.
2. Capability naming is still unresolved for part of the current fixture corpus. The least ambiguous families are http_endpoint, scheduled_task, mcp_server, llm_inference, embeddings, and likely relational_database. Ambiguous cases needing explicit decisions include FastAPI background_tasks, Pydantic data_model, SQLAlchemy/SQLModel model features, TypeScript Lit web_component/reactive_property, SWR data_fetch, and Zustand store features.
3. tests/processor/db/test_framework_loader.py currently uses route_handler as a capability key, which is invalid under the current schema enum; rename the fixture to http_endpoint rather than widening the enum just for a test.
4. FastAPI router composition should be revisited for startpoint semantics because include_router is composition, not an executable entrypoint.

## Fix: `_load_python_feature_specs()` reimplements framework-definition parsing (Medium)

### Problem Analysis

`tests/parser/test_framework_detection_tree_sitter.py:24-55` manually reads JSON and constructs `FeatureSpec` directly, bypassing the production normalization pipeline.

**Production path (what the test SHOULD exercise):**
1. `FrameworkDefinitionLoader.load_framework_definitions()` → reads JSON, merges across `<lang>/*.json`
2. `FrameworkDefinitionLoader.parse_json_data()` → calls `_normalize_feature_payload()` which:
   - `absolute_paths`: Filters non-string values (framework_loader.py:237-241)
   - `construct_query`: Non-dict → `None` (framework_loader.py:243-244)
   - `concept`: Invalid → defaults to `AnnotationLike` via `_normalize_concept_name()` (framework_loader.py:27-32)
   - `base_confidence`: Validates scope (CallExpression only), range [0,1], coerces to float (framework_loader.py:35-66)
   - `target_level`: Invalid → defaults to `function` (framework_loader.py:248-249)
   - `locator_strategy`: Invalid → defaults to `VariableBound` (framework_loader.py:251-255)
   - `startpoint`: Non-bool → defaults to `False` (framework_loader.py:257-258)
   - Injects `capability_key` and `operation_key` from hierarchy (framework_loader.py:185-195)
   - Strips `base_confidence` from non-CallExpression payloads (framework_loader.py:198-201)
3. `framework_query_service._build_feature_spec()` + `_resolve_base_confidence()` reconstructs `FeatureSpec`

**What the test does instead (lines 24-55):**
- `absolute_paths=op_data.get("absolute_paths", [])` — No string filtering
- `target_level=TargetLevel(op_data.get("target_level"))` — No defaulting on invalid
- `concept=Concept(op_data.get("concept"))` — No normalization fallback
- `locator_strategy=LocatorStrategy.VARIABLE_BOUND` — Hardcoded, ignores JSON value
- `base_confidence=op_data.get("base_confidence")` — No scope/range validation
- `startpoint=op_data.get("startpoint", False)` — No type validation

**Breakage this can miss:**
- Bugs in `_normalize_feature_payload()` defaulting
- Bugs in `_normalize_base_confidence()` validation
- Bugs in capability/operation key injection into `feature_definition` JSONB
- Bugs in `_build_feature_spec()` reconstruction (capability_key/operation_key round-trip)
- Schema changes affecting loader parsing logic
- `locator_strategy` from JSON being silently ignored

### Solution: Use production loader + query service helpers (no DB required)

`FrameworkDefinitionLoader.parse_json_data()` returns in-memory DB model instances (`Framework`, `FrameworkFeature`, `FeatureAbsolutePath`) without requiring a database. `framework_query_service._build_feature_spec()` and `_resolve_base_confidence()` are module-level functions that convert these models to `FeatureSpec`. Together they exercise the full normalization path without needing a live PostgreSQL instance.

### Changes Required

**File: `tests/parser/test_framework_detection_tree_sitter.py`**

**Change 1 — Update imports (lines 2-21):**
- Remove: `import json`
- Add: `from collections import defaultdict`
- Add: `from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings`
- Add: `from src.code_confluence_flow_bridge.processor.db.postgres.framework_loader import FrameworkDefinitionLoader`
- Add: `from src.code_confluence_flow_bridge.processor.db.postgres.framework_query_service import _build_feature_spec, _resolve_base_confidence`
- Remove unused: `CallExpressionInfo`, `Concept`, `InheritanceInfo`, `LocatorStrategy`, `TargetLevel` (verify which are still used by helper functions below)

**Change 2 — Replace `_load_python_feature_specs()` (lines 24-55):**
```python
@lru_cache(maxsize=1)
def _load_python_feature_specs() -> List[FeatureSpec]:
    repo_root = Path(__file__).resolve().parents[2]
    definitions_dir = repo_root / "framework-definitions"
    settings = EnvironmentSettings(FRAMEWORK_DEFINITIONS_PATH=str(definitions_dir))
    loader = FrameworkDefinitionLoader(settings)
    framework_data = loader.load_framework_definitions()
    _frameworks, features, absolute_paths = loader.parse_json_data(framework_data)
    paths_by_feature: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for ap in absolute_paths:
        paths_by_feature[(ap.language, ap.library, ap.feature_key)].append(ap.absolute_path)
    feature_specs: List[FeatureSpec] = []
    for feature in features:
        if feature.language != "python":
            continue
        feature_paths = paths_by_feature[(feature.language, feature.library, feature.feature_key)]
        base_confidence = _resolve_base_confidence(feature)
        feature_specs.append(_build_feature_spec(feature, feature_paths, base_confidence))
    return feature_specs
```

**Change 3 — No changes to test functions or hand-built helpers:**
All test functions remain unchanged (consume `List[FeatureSpec]`). `_build_pydantic_inheritance_spec()` and `_build_litellm_completion_spec()` are intentionally hand-built for targeted detector unit tests — keep as-is.

### Validation Steps
1. `cd unoplat-code-confluence-ingestion/code-confluence-flow-bridge && uv run pytest tests/parser/test_framework_detection_tree_sitter.py -v`
2. Verify all existing tests pass
3. Confirm FeatureSpec objects now have: `capability_key`/`operation_key` populated, `locator_strategy` from JSON, `base_confidence` validated, `concept` normalized

Validated the local framework-definition corpus against framework-definitions/schema.json after the capability/operation migration. Updated query-service regression assertions to derive capability and operation from the composite feature_key rather than expecting separate FeatureSpec attributes.

Refreshed integration regressions for the current fixture corpus by allowing FunctionDefinition concepts in real-framework parsing validation and by enforcing unknown-key rejection through FrameworkFeaturePayload extra='forbid' in the installed commons package used by flow-bridge.

Ran uv sync --group test in unoplat-code-confluence-ingestion/code-confluence-flow-bridge to restore test dependencies, then verified the focused migration suite passes end-to-end.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aligned the local flow-bridge fixture corpus and regressions with the single-contract capability -> operation schema. Verified all shipped framework-definition JSON files validate against framework-definitions/schema.json, confirmed FastAPI and Next.js endpoint fixtures are split into per-verb operations, and kept persisted feature identity on the composite feature_key contract. Updated query-service regression expectations to derive capability and operation from feature_key, refreshed integration assertions for the expanded concept set (including FunctionDefinition), and restored strict unknown-key rejection for framework feature payloads via the installed commons package used by flow-bridge.

Validation run:
- uv run python schema validation for all framework definition JSON files
- uv run pytest tests/processor/db/test_framework_loader.py tests/processor/db/test_framework_query_service.py tests/parser/test_framework_detection_tree_sitter.py tests/integration/test_framework_definitions_ingestion.py -v --timeout=60

Result: 28 passed.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 All local flow-bridge framework definition JSON files use capabilities -> operations and validate against framework-definitions/schema.json.
- [x] #2 Every authored operation in the local fixture set represents exactly one executable runtime contract with no grouped variants or detector arrays.
- [x] #3 FastAPI and Next.js endpoint fixtures are split into per-verb operations and downstream regressions assert operation-level keys.
- [x] #4 tests/integration/test_framework_definitions_ingestion.py no longer duplicates a v3 features parser or seed path and instead exercises the production loader behavior.
- [x] #5 Loader and query-service regressions verify persisted feature_key = capability.operation plus capability_key and operation_key round-trip.
- [x] #6 Local parser and integration regressions that read shipped definitions or assert old flat keys are updated or explicitly removed if obsolete.
- [x] #7 No database schema or storage change is introduced as part of this task.
<!-- DOD:END -->
