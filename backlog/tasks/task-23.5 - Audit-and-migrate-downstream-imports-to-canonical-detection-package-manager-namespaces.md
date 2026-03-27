---
id: TASK-23.5
title: >-
  Audit and migrate downstream imports to canonical detection/package-manager
  namespaces
status: Done
assignee:
  - OpenCode
created_date: '2026-03-27 10:37'
updated_date: '2026-03-27 12:41'
labels:
  - backend
  - refactor
  - python
  - typescript
  - package-manager
  - detection
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/
documentation:
  - doc-1
parent_task_id: TASK-23
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all in-repo downstream consumers to import from the canonical `models.detection.{shared,python,typescript}` and `parser.package_manager.{shared,python,typescript}` namespaces. Do not add shim-based re-exports or compatibility aliases; the codebase should fully adopt the new canonical imports.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All in-repo imports referencing legacy TASK-23 module paths are replaced with canonical detection and package-manager namespace imports.
- [x] #2 No shim-based re-exports or compatibility alias modules are added to preserve old import paths.
- [x] #3 Repository searches confirm there are no remaining downstream consumers of the retired TASK-23 import paths in production code or tests.
- [x] #4 Targeted verification for the touched import consumers passes.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Move `parser/package_manager/detectors/ordered_detection.py` into the canonical shared namespace as `parser/package_manager/shared/ordered_detection.py`.
2. Update all in-repo consumers in python/typescript detector modules to import `OrderedDetector` from the shared canonical path.
3. Remove the retired `parser/package_manager/detectors` import surface if it no longer has active consumers.
4. Verify with repo searches for stale imports plus focused basedpyright/Ruff/pytest coverage for touched files.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed the direct in-repo import migration to canonical detection/package-manager namespaces without adding shims. The remaining `ordered_detection` surface now lives under `src/code_confluence_flow_bridge/parser/package_manager/shared/ordered_detection.py`, and repository searches show no in-repo consumers of the retired import path.

Final polish pass also normalized the TypeScript package.json strategy naming by renaming `NodePackageManagerStrategy` to `TypeScriptPackageJsonStrategy` and updating the registry, tests, and docs accordingly.

Verification for the migrated consumers is clean: focused `basedpyright` passed for the renamed TypeScript strategy surface, `ruff check` passed, and `uv run --group test pytest tests/parser/package_manager/ -v` passed with `83 passed`.
<!-- SECTION:NOTES:END -->
