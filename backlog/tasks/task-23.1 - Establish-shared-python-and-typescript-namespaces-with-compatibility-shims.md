---
id: TASK-23.1
title: 'Establish shared, python, and typescript namespaces with compatibility shims'
status: Done
assignee: []
created_date: '2026-03-25 13:19'
updated_date: '2026-03-27 05:59'
labels:
  - backend
  - refactor
  - architecture
  - package-manager
  - detection
  - python
  - typescript
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/configuration/settings.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/
documentation:
  - doc-1
parent_task_id: TASK-23
priority: medium
ordinal: 2310
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the destination package structure for detection and package-manager code, and move the lowest-risk shared primitives first so later relocations have stable canonical homes. This phase is a structure-only foundation and should not intentionally change detector or package-metadata behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Destination packages for `models/detection/{shared,python,typescript}` and `parser/package_manager/{shared,python,typescript}` exist with clear canonical ownership.
- [x] #2 Shared detection primitives needed by both languages have canonical homes outside `models/configuration/settings.py`.
- [x] #3 Legacy import locations continue to resolve through compatibility shims or equivalent transitional modules during the migration.
- [x] #4 Low-risk import updates land without intended runtime behavior changes, and targeted verification for the moved primitives passes.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Phase 1 foundation steps:
1. Create the new package directories and `__init__.py` files for `models/detection/{shared,python,typescript}` and `parser/package_manager/{shared,python,typescript}`.
2. Move the safest shared detection primitives first: `FileNode`, `Signature`, `ManagerRule`, and `LanguageRules` into canonical shared detection modules.
3. Replace the old definitions or old module homes with compatibility re-export shims so existing imports keep working.
4. Update only the lowest-risk imports in touched modules; avoid large sweep edits in this phase.
5. Verify no intended runtime behavior changes before marking this phase complete.

Definition of success for this phase: the destination namespaces exist and the first shared primitives have stable canonical homes outside `settings.py`.
<!-- SECTION:PLAN:END -->
