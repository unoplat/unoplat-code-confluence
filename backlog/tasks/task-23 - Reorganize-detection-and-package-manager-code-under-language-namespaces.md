---
id: TASK-23
title: Reorganize detection and package-manager code under language namespaces
status: Done
assignee:
  - OpenCode
created_date: '2026-03-25 13:18'
updated_date: '2026-03-27 12:45'
labels:
  - backend
  - refactor
  - architecture
  - python
  - typescript
  - package-manager
  - detection
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/configuration/settings.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/
documentation:
  - doc-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reorganize detection models, detector helpers, manifest loaders, and package-manager strategies so Python- and TypeScript-specific code lives under canonical `python` and `typescript` namespaces, while only truly shared abstractions remain in `shared`. The end state is a no-shim structure that is easier to navigate and maintain, with downstream consumers updated directly to canonical imports.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `models/detection` and `parser/package_manager` are organized around canonical `shared`, `python`, and `typescript` namespaces that mirror the language-oriented engine structure.
- [x] #2 Detection-specific shared primitives are no longer owned by `models/configuration/settings.py`; they are moved to canonical detection modules or removed if dead.
- [x] #3 Flat or ecosystem-named parser namespaces such as `node`, `pip`, `poetry`, and `uv` are no longer the canonical homes for language-specific package-manager code; direct consumers now use the canonical language-oriented modules.
- [x] #4 The migration is completed without shim-based re-exports or compatibility aliases for in-repo consumers; repository searches confirm retired TASK-23 import paths are no longer used in source or tests.
- [x] #5 Targeted verification for the reorganized detection/package-manager surface passes (focused basedpyright, Ruff, and package-manager regression tests), and broader repo-level verification findings are documented as follow-up debt outside TASK-23 scope.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Execution plan approved for no-shim follow-up cleanup.

Sequence:
1. TASK-23.5 - Move remaining in-repo downstream consumers to canonical package-manager/detection namespaces, including moving `parser/package_manager/detectors/ordered_detection.py` into `parser/package_manager/shared/ordered_detection.py` and updating all repo consumers.
2. TASK-23.7 - Remove dead detection seams after import migration, including deleting `CodebaseDetection` if still unused and removing package-level re-export surfaces that are no longer needed in-repo.
3. TASK-23.6 - Clean up TASK-23 verification hygiene by aligning package-manager tests with the canonical `typescript` namespace and fixing Ruff/test-package issues.
4. TASK-23.8 - Resolve the remaining TASK-23 package-manager typing failures in canonical python/typescript modules and direct integration points, then rerun basedpyright, Ruff, and package-manager regression tests.

Constraints:
- Do not add shim-based re-exports or compatibility aliases.
- Update downstream consumers directly to canonical imports.
- Keep types precise and avoid `Any` escape hatches.
- Verification order is basedpyright first, Ruff second, then relevant pytest coverage.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Primary implementation document: `doc-1` (Detection and package-manager namespace reorganization plan).

Important constraint from product direction: use `typescript/` as the namespace for Node/package.json code for now. Do not introduce a `node/` canonical namespace in the new layout.

Review guidance: keep each PR narrowly scoped to a single phase so reviewers can separate structural churn from any accidental behavior change.

Scheduling note: `TASK-23.3` and `TASK-23.2` touch the same TypeScript detector/model surfaces as `TASK-16.9.1`. Prefer to start those phases after rebasing on the latest `TASK-16.9.1` implementation or after that task lands, to reduce structural merge conflicts.

Verification/fix loop resumed and completed for the remaining TASK-23 typing and package-manager hygiene work. Focused `basedpyright` is now clean for the touched integration points, targeted `ruff check` passes, and `uv run --group test pytest tests/parser/package_manager/ -v` passed with `83 passed`.

Final polish pass normalized the remaining TypeScript strategy naming (`TypeScriptPackageJsonStrategy`), updated the package-manager registry/tests/docs, and reconfirmed there are no source references to retired TASK-23 import paths such as `NodePackageManagerStrategy`, `parser/package_manager/node`, `parser.package_manager.detectors.ordered_detection`, or `CodebaseDetection`.

Broader repo-level verification was run after TASK-23 completion using a general agent from the flow-bridge project root. Results: `uv run --group dev basedpyright src/` failed with substantial pre-existing repo-wide typing debt (`391 errors, 4 warnings`), `uv run ruff check src/` failed with 4 unrelated repo-level issues (including a relative import in `src/code_confluence_flow_bridge/github_app/service.py` and import ordering in both ripgrep detector modules), and `uv run --group test pytest tests/parser/ -v` ended with `101 passed, 4 errors` due to Docker-unavailable test setup in `tests/parser/test_framework_detection_language_processor.py`.

These broader verification failures are not specific regressions from TASK-23; the reorganized detection/package-manager slice remains locally stable with targeted verification green and no remaining legacy source references to retired TASK-23 import paths.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed the detection and package-manager namespace reorganization around canonical `shared`, `python`, and `typescript` packages, and finished the no-shim migration by updating downstream consumers directly to the new module homes. The final polish removed dead detection seams such as `CodebaseDetection`, retired the remaining `ordered_detection` legacy import surface, normalized the TypeScript package.json strategy naming to `TypeScriptPackageJsonStrategy`, and aligned tests/docs to the canonical TypeScript namespace.

Why: the previous flat and ecosystem-oriented layout made ownership harder to understand and encouraged transitional import seams to linger. The new structure makes language-specific responsibilities obvious to contributors, reduces cross-module ambiguity, and leaves only truly shared abstractions in shared packages.

Verification completed for TASK-23 scope in the required order: focused `basedpyright` passed for the touched detection/package-manager integration points, targeted `ruff check` passed, and `uv run --group test pytest tests/parser/package_manager/ -v` passed with `83 passed`. A broader repo-level verification pass was also run and documented; it surfaced unrelated repo-wide typing, lint, and Docker-dependent test issues outside TASK-23 scope, but did not indicate new instability in the reorganized slice.
<!-- SECTION:FINAL_SUMMARY:END -->
