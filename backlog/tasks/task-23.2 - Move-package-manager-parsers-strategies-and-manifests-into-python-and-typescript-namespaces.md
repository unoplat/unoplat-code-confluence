---
id: TASK-23.2
title: >-
  Move package-manager parsers, strategies, and manifests into python and
  typescript namespaces
status: Done
assignee: []
created_date: '2026-03-25 13:19'
updated_date: '2026-03-27 10:23'
labels:
  - backend
  - refactor
  - package-manager
  - python
  - typescript
dependencies:
  - TASK-23.1
  - TASK-23.3
  - TASK-16.9.1
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/package_manager_parser.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/package_manager_factory.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/package_manager_strategy.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/node/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/pip/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/poetry/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/uv/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/
documentation:
  - doc-1
parent_task_id: TASK-23
priority: medium
ordinal: 2330
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reorganize `parser/package_manager` so Python and TypeScript responsibilities live under their language namespaces, while shared orchestration seams and truly generic helpers remain in a small shared package. This phase should make `node`, `pip`, `poetry`, and `uv` non-canonical legacy paths.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Shared parser seams such as the package-manager parser, strategy interface, registry/factory, and generic helpers have canonical homes under `parser/package_manager/shared/`.
- [ ] #2 Python package-manager detectors, strategies, and manifest helpers have canonical homes under `parser/package_manager/python/`.
- [ ] #3 TypeScript package-manager detectors, package-json strategy, and package-json manifest helpers have canonical homes under `parser/package_manager/typescript/`.
- [ ] #4 Legacy parser locations remain only as transitional shims until imports are updated, and targeted Python and TypeScript package-manager verification passes.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Phase 3 parser/package-manager relocation steps:
1. Move shared parser seams (`PackageManagerParser`, strategy interface, registry/factory, generic git/ripgrep helpers) into `parser/package_manager/shared/`.
2. Move Python-specific detectors, strategies, and manifest/config helpers into `parser/package_manager/python/`.
3. Move TypeScript-specific detectors, package-json strategy, and package-json loader into `parser/package_manager/typescript/`.
4. Split mixed helpers such as `ripgrep_utils.py` so only truly generic ripgrep wrappers remain shared.
5. Update central imports in the factory/parser/orchestration layers and verify both Python and TypeScript package-manager paths.

Important naming rule: the current `node/` package becomes a legacy shim; the new canonical home is under `typescript/`.
<!-- SECTION:PLAN:END -->
