---
id: TASK-23.8
title: >-
  Resolve package-manager refactor type failures in canonical python/typescript
  modules
status: Done
assignee:
  - OpenCode
created_date: '2026-03-27 10:37'
updated_date: '2026-03-27 11:22'
labels:
  - backend
  - refactor
  - python
  - typescript
  - package-manager
  - typing
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/package_metadata_activity/package_manager_metadata_activity.py
documentation:
  - doc-1
parent_task_id: TASK-23
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Clear the basedpyright failures introduced or exposed by the package-manager namespace refactor, especially in the canonical python/typescript detector, strategy, and manifest modules and any direct integration points such as `main.py` or package metadata activity wiring. Keep types precise and avoid `Any`-based shortcuts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Basedpyright passes for the package-manager namespace surfaces touched by TASK-23, including canonical python/typescript modules and direct integration points touched by the refactor.
- [x] #2 Known current failures in files such as `python/detectors/ripgrep_detector.py`, `python/managers/pip_strategy.py`, `python/managers/poetry_strategy.py`, and equivalent touched modules are resolved with precise typing.
- [x] #3 The implementation does not rely on shim re-exports or `Any`-typed escape hatches to satisfy the checker.
- [x] #4 Relevant package-manager regression tests pass after the typing fixes.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Fix the TASK-23-specific path/type mismatch in `python/detectors/ripgrep_detector.py`.
2. Add precise intermediate typing to `python/managers/pip_strategy.py` without changing include/source-file behavior.
3. Add narrowing helpers and precise manifest typing to `python/managers/poetry_strategy.py`, including removing the undefined `group` reference.
4. Tighten activity/logger typing in `main.py`, `utility/deps.py`, and `utility/detection.py`.
5. Re-run targeted basedpyright first, then Ruff, then package-manager regression tests.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Cleared the targeted basedpyright failures in `src/code_confluence_flow_bridge/parser/package_manager/python/detectors/ripgrep_detector.py`, `src/code_confluence_flow_bridge/parser/package_manager/python/managers/pip_strategy.py`, `src/code_confluence_flow_bridge/parser/package_manager/python/managers/poetry_strategy.py`, `src/code_confluence_flow_bridge/main.py`, and the logger helper wiring.

Kept the fixes shim-free and precise by tightening TypedDict access, coercion helpers, and logger protocol usage instead of introducing compatibility aliases or `Any` escape hatches.

Post-fix verification is green: focused `basedpyright` returned `0 errors`, targeted `ruff check` passed, and `uv run --group test pytest tests/parser/package_manager/ -v` passed with `83 passed`.
<!-- SECTION:NOTES:END -->
