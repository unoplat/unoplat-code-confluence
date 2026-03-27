---
id: TASK-23.4
title: >-
  Retire legacy layout seams and finish symmetry between Python and TypeScript
  rules loading
status: Done
assignee: []
created_date: '2026-03-25 13:19'
updated_date: '2026-03-27 10:22'
labels:
  - backend
  - refactor
  - package-manager
  - python
  - typescript
  - cleanup
dependencies:
  - TASK-23.2
  - TASK-23.3
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/python_ripgrep_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/typescript_rules_loader.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/rules.yaml
documentation:
  - doc-1
parent_task_id: TASK-23
priority: medium
ordinal: 2340
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Finish the reorganization by removing temporary legacy import seams once the new canonical layout is fully adopted, and close the remaining architectural asymmetry between Python and TypeScript rules loading. This phase should leave the codebase in a steady state that a junior developer can navigate without tribal knowledge.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Python and TypeScript detection/rules-loading paths follow the same high-level architectural pattern where practical.
- [x] #2 Temporary compatibility shims and legacy flat import paths are removed or explicitly isolated behind a final follow-up task.
- [x] #3 No live code depends on `node`, `pip`, `poetry`, `uv`, or flat detection modules as canonical implementation homes.
- [x] #4 Full verification for the reorganized detection and package-manager stack passes after cleanup.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Phase 4 symmetry and cleanup steps:
1. Add a typed Python rules loader so Python and TypeScript follow the same high-level rules-loading structure where practical.
2. Finish migrating remaining imports to canonical shared/python/typescript locations.
3. Remove temporary compatibility shims and legacy namespace modules once no live imports depend on them.
4. Run a broader verification pass covering the reorganized detection and package-manager stack.
5. If any shim cannot be safely removed, capture the reason and create a clearly scoped follow-up task instead of leaving an undocumented partial state.

Definition of success for this phase: a new contributor can navigate the detection and package-manager stack by language namespace without needing tribal knowledge about old flat roots.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## Summary

Retired all legacy layout seams and achieved full symmetry between Python and TypeScript rules loading.

### AC#1 — Python/TypeScript symmetry
- Created `models/detection/python/rules.py` with typed Pydantic config models (`RuleSignatureConfig`, `RuleManagerConfig`, `LanguageRulesConfig`, `RulesFileConfig`) mirroring TypeScript's structure
- Created `parser/package_manager/python/detectors/rules_loader.py` with `load_python_language_rules()` — same Pydantic-validated YAML loading pattern as TypeScript's `load_typescript_language_rules()`
- Updated `python/detectors/ripgrep_detector.py` to use the new loader, removing inline `_load_rules()` with raw dict parsing

### AC#2 & AC#3 — Shim removal and import migration
- Migrated 11 files (4 src + 7 tests) from old shim paths to canonical `shared/`, `python/`, `typescript/` paths
- Removed 18 parser shim files, 4 model shim files, and 1 duplicate `detectors/rules.yaml`
- Removed 5 detection model re-exports from `settings.py`
- Deleted 5 empty legacy directories (`pip/`, `poetry/`, `uv/`, `node/`, `utils/`)
- Zero internal consumers remain on any old path

### AC#4 — Verification
- basedpyright: 0 new errors (530 pre-existing, none in changed files)
- ruff: 0 new errors (2 pre-existing TID252 in unrelated file)
- pytest: 83/83 passed
<!-- SECTION:FINAL_SUMMARY:END -->
