---
id: TASK-23.6
title: Clean up TASK-23 verification and test-package hygiene
status: Done
assignee:
  - OpenCode
created_date: '2026-03-27 10:37'
updated_date: '2026-03-27 11:22'
labels:
  - backend
  - refactor
  - tests
  - lint
  - package-manager
  - detection
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/package_manager/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/
documentation:
  - doc-1
parent_task_id: TASK-23
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Repair the remaining verification gaps around the namespace reorganization, including Ruff failures, test import ordering, and package/test layout issues in TASK-23-touched areas. End state should be a clean targeted verification loop for the reorganized package-manager and detection code.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Ruff issues in TASK-23-touched files and tests are resolved.
- [x] #2 Test package layout and import hygiene are consistent with the canonical namespace reorganization.
- [x] #3 The targeted TASK-23 verification loop runs cleanly in the required order: basedpyright, Ruff, then relevant regression tests.
- [x] #4 Verification artifacts clearly demonstrate there are no remaining TASK-23-specific lint or test-package hygiene gaps.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Fix Ruff import ordering in `tests/parser/package_manager/test_package_manager_factory.py`.
2. Replace the legacy `tests/parser/package_manager/node/` package with a canonical `tests/parser/package_manager/typescript/` package and align test names/fixtures accordingly.
3. Update any affected test-data paths and imports.
4. Re-run focused basedpyright, Ruff, and package-manager pytest verification for the test surface.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Aligned the package-manager test surface to the canonical `typescript` namespace, including moving the former `tests/parser/package_manager/node/` tests and fixture paths to `tests/parser/package_manager/typescript/` and adding the package marker.

Resolved Ruff hygiene in TASK-23-touched verification files, including `tests/parser/package_manager/test_package_manager_factory.py`, and reran the required verification order successfully.

Verification run completed cleanly in the required order from the flow-bridge project root: `uv run --group dev basedpyright ...` -> `uv run ruff check ...` -> `uv run --group test pytest tests/parser/package_manager/ -v` with `83 passed`.
<!-- SECTION:NOTES:END -->
