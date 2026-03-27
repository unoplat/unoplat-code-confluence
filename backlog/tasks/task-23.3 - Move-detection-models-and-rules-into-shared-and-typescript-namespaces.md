---
id: TASK-23.3
title: Move detection models and rules into shared and typescript namespaces
status: Done
assignee: []
created_date: '2026-03-25 13:19'
updated_date: '2026-03-27 06:15'
labels:
  - backend
  - refactor
  - detection
  - typescript
  - package-manager
dependencies:
  - TASK-23.1
  - TASK-16.9.1
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/detected_codebase.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/package_manager_detection.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript_detection.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript_rules.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/configuration/settings.py
documentation:
  - doc-1
parent_task_id: TASK-23
priority: medium
ordinal: 2320
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Relocate flat detection models and TypeScript-specific discovery/rules types into the new language-oriented model structure so detection ownership is obvious to a new contributor. This phase should remove detection-model ownership from `settings.py` and the flat `models/detection` root without changing current detector decisions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 TypeScript-specific discovery and rules models live under `models/detection/typescript/`, and shared detection primitives live under `models/detection/shared/`.
- [x] #2 `models/configuration/settings.py` no longer acts as the canonical home for detection-specific models.
- [x] #3 Detector modules and tests import from the new canonical model locations or sanctioned compatibility shims.
- [x] #4 Detection-model relocation preserves existing detector behavior and passes targeted verification.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Phase 2 detection-model relocation steps:
1. Move `DetectedCodebase` and package-manager evidence models into shared detection modules.
2. Move TypeScript-specific discovery models into `models/detection/typescript/discovery.py`.
3. Split generic rule primitives from TypeScript-only rules/config models.
4. Remove canonical detection-model ownership from `models/configuration/settings.py`; keep compatibility shims where needed.
5. Update detector/test imports to canonical model locations and run targeted verification.

Keep class names stable during this phase unless a rename is required to resolve an immediate collision. Structural clarity matters more than semantic renaming here.
<!-- SECTION:PLAN:END -->
