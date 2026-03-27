---
id: TASK-16.9.1
title: >-
  Ingestion: preserve TypeScript monorepo metadata through detection and
  persistence
status: In Progress
assignee: []
created_date: '2026-03-23 07:04'
updated_date: '2026-03-23 07:42'
labels:
  - backend
  - typescript
  - monorepo
  - ingestion
  - bug
  - task-16
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/typescript_ripgrep_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/detected_codebase.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/repository/mappers.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/programming_language_metadata.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/package_manager/detectors/test_typescript_ripgrep_detector.py
parent_task_id: TASK-16.9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Preserve package-manager provenance, workspace_root, manifest_path, and project_name for detected TypeScript workspaces across detector output, CodebaseConfig persistence, and repository API reconstruction.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 TypeScript detector emits effective package manager, package_manager_provenance, and workspace_root for inherited and local-owner cases.
- [ ] #2 Mixed-manager nested workspace detection prefers child-local manager ownership over inherited parent ownership when local signals exist.
- [ ] #3 Persisted CodebaseConfig metadata round-trips package_manager_provenance and workspace_root without breaking older rows or standalone projects.
- [ ] #4 Regression coverage in `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/package_manager/detectors/test_typescript_ripgrep_detector.py` verifies t3code inherited Bun workspaces, nested aggregators, and a child-local override case.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Tighten the TypeScript detector payload so emitted codebases always carry effective manager, provenance, and nearest workspace owner.
2. Verify `_find_aggregator_manager()` and nested workspace resolution use nearest-owner semantics.
3. Preserve the new fields when building `ProgrammingLanguageMetadata` and reconstructing metadata from stored JSONB.
4. Extend detector regressions with explicit assertions for provenance and workspace_root.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Investigated current detector regression. The existing t3code detector test already fails locally: workspace members are being re-detected as local `npm` because the npm fallback rule matches any leaf `package.json` when lockfile names are absent from that file's contents. Planning to tighten the test assertions and add detector logging around local-vs-inherited resolution so the mismatch is visible in test output and production logs.

Added structured manager-match logging in `ordered_detection.py`, workspace-ownership decision logging plus cache-build logs in `typescript_ripgrep_detector.py`, and strengthened `test_typescript_ripgrep_detector.py` to assert `package_manager_provenance` and `workspace_root` for t3code, nested workspace ownership, pnpm workspace inheritance, and an explicit child-local override case. Targeted detector test file now passes end-to-end.

Targeted typecheck on the touched detector files still reports pre-existing `basedpyright` issues in `typescript_ripgrep_detector.py`'s older YAML parsing paths (unknown-typed locals around `_load_rules` and `_read_workspace_globs`), while lint for the touched files passes after import normalization.
<!-- SECTION:NOTES:END -->
