---
id: TASK-23.7
title: Remove dead detection seams and finish detection namespace cleanup
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
  - detection
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/configuration/settings.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/
documentation:
  - doc-1
parent_task_id: TASK-23
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Finish the detection-side cleanup after the namespace reorganization. Detection primitives should live only in canonical detection modules, dead seams such as `CodebaseDetection` should be removed if unused, and downstream detection consumers should be updated directly rather than preserved through re-export shims.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Detection models and rules are owned by canonical detection modules rather than `models/configuration/settings.py`.
- [x] #2 Dead detection seams introduced or retained during TASK-23, including `CodebaseDetection` if it has no real callers, are removed with callers updated accordingly.
- [x] #3 Detection-related imports across the repository use canonical modules without re-export shims.
- [x] #4 Type checking and relevant detection/package-manager verification pass for touched files.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm there are no live in-repo callers of `CodebaseDetection` or package-level detection re-export seams.
2. Remove dead detection constructs from canonical detection modules, keeping `DetectedCodebase` as the shared result model.
3. Simplify `models/detection/shared/__init__.py` and `models/detection/typescript/__init__.py` so they no longer act as compatibility surfaces.
4. Re-run targeted searches and focused verification for touched detection/package-manager files.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Confirmed there are no live in-repo callers of `CodebaseDetection` or the retired detection/package-level re-export seams; repository searches for `CodebaseDetection` and legacy detection import patterns now return no source matches.

Detection ownership is now centered in canonical detection modules under `src/code_confluence_flow_bridge/models/detection/{shared,python,typescript}`, with dead seams removed and no dependency on `models/configuration/settings.py` for detection primitives.

Post-cleanup verification remains green alongside the package-manager regression pass: focused typecheck and lint succeeded, and `uv run --group test pytest tests/parser/package_manager/ -v` passed with `83 passed`.
<!-- SECTION:NOTES:END -->
