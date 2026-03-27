---
id: doc-1
title: Detection and package-manager namespace reorganization plan
type: other
created_date: '2026-03-25 13:17'
---
# Goal

Reorganize detection and package-manager code so language-specific concerns live under language namespaces that mirror the existing `engine/programming_language/{python,typescript}` structure.

The target outcome is a codebase where a developer can answer these questions quickly:
- Where do TypeScript detection models live?
- Where do Python package-manager strategies live?
- Which code is truly shared across languages?
- Which files are compatibility shims scheduled for removal?

This plan is intentionally detailed enough for a junior developer to execute in small, reviewable phases without changing behavior accidentally.

# Constraints

- Use `typescript/` as the Node/TypeScript namespace for now.
- Keep only a very small shared core at the top level.
- Preserve behavior while reorganizing; this is a structure-first refactor, not a feature change.
- Do not mix detection-specific models into `models/configuration/settings.py` after the migration.
- Prefer staged compatibility shims over a flag day rename.
- Update imports incrementally and verify each phase before continuing.

# Design principles

1. Organize by programming language first, then by responsibility.
2. Keep shared abstractions only when they are used by both Python and TypeScript.
3. Keep models as typed data containers; keep file reading/parsing logic in parser modules.
4. Mirror package layout between `models/detection` and `parser/package_manager` where practical.
5. Avoid renaming runtime behavior and structure in the same phase unless required.
6. Preserve stable public seams until all consumers are moved.

# Target package layout

## `models/detection`

```text
models/detection/
  __init__.py
  shared/
    __init__.py
    inventory.py
    evidence.py
    results.py
    rules.py
  python/
    __init__.py
    discovery.py
    rules.py
    manifests.py
    package_metadata.py
  typescript/
    __init__.py
    discovery.py
    rules.py
    manifests.py
    package_metadata.py
```

### Shared responsibilities

- `inventory.py`
  - `FileNode`
- `evidence.py`
  - current `ManagerDetectionResult` replacement or home
- `results.py`
  - current `DetectedCodebase` replacement or home
- `rules.py`
  - generic rule primitives used by both languages
  - `Signature`
  - `ManagerRule`
  - `LanguageRules`
  - optionally generic rules-file wrappers if both languages converge on the same loader pattern

### Python responsibilities

- `discovery.py`
  - Python-specific scan/discovery result types if needed
- `rules.py`
  - typed Python rules-file models if Python gets parity with TypeScript rules loading
- `manifests.py`
  - typed `pyproject.toml`, requirements, or setup metadata views that belong in models rather than parser helpers
- `package_metadata.py`
  - Python-specific package metadata helper models if needed

### TypeScript responsibilities

- `discovery.py`
  - `WorkspaceOrchestratorMetadata`
  - `WorkspaceDiscoveryContext`
  - `TypeScriptRepositoryScan`
- `rules.py`
  - `WorkspacePackagesConfig`
  - `PnpmWorkspaceConfig`
  - any TypeScript-only rules-file wrappers
- `manifests.py`
  - `PackageJsonManifest` and related typed manifest shapes
- `package_metadata.py`
  - TypeScript/package.json-specific package metadata helper models if needed

## `parser/package_manager`

```text
parser/package_manager/
  __init__.py
  shared/
    __init__.py
    parser.py
    registry.py
    strategy.py
    git_utils.py
    ripgrep.py
  python/
    __init__.py
    detectors/
      __init__.py
      ripgrep_detector.py
      rules_loader.py
    managers/
      __init__.py
      pip_strategy.py
      poetry_strategy.py
      uv_strategy.py
    manifests/
      __init__.py
      pyproject_loader.py
      requirements_loader.py
      setup_parser.py
  typescript/
    __init__.py
    detectors/
      __init__.py
      ripgrep_detector.py
      monorepo_detection_adapter.py
      standalone_detection_adapter.py
      workspace_utils.py
      rules_loader.py
    managers/
      __init__.py
      package_json_strategy.py
    manifests/
      __init__.py
      package_json_loader.py
```

### Shared parser responsibilities

- `parser.py`
  - current `PackageManagerParser`
- `registry.py`
  - current `PackageManagerStrategyFactory`
- `strategy.py`
  - current `PackageManagerStrategy`
- `git_utils.py`
  - generic repo clone/path helpers
- `ripgrep.py`
  - generic ripgrep wrappers only

### Python parser responsibilities

- `detectors/ripgrep_detector.py`
  - current `python_ripgrep_detector.py`
- `detectors/rules_loader.py`
  - typed Python rules loader to match TypeScript structure
- `managers/`
  - `pip_strategy.py`
  - `poetry_strategy.py`
  - `uv_strategy.py`
- `manifests/`
  - manifest/config readers that are Python-specific

### TypeScript parser responsibilities

- `detectors/ripgrep_detector.py`
  - current `typescript_ripgrep_detector.py`
- `detectors/monorepo_detection_adapter.py`
  - current `typescript_monorepo_detection_adapter.py`
- `detectors/standalone_detection_adapter.py`
  - current `typescript_standalone_detection_adapter.py`
- `detectors/workspace_utils.py`
  - current `typescript_detection_utils.py`
- `detectors/rules_loader.py`
  - current `typescript_rules_loader.py`
- `managers/package_json_strategy.py`
  - current `node_package_manager_strategy.py`
- `manifests/package_json_loader.py`
  - current `package_json_loader.py`

# Current-to-target file mapping

## Models

- `models/detection/detected_codebase.py`
  - target: `models/detection/shared/results.py`
- `models/detection/package_manager_detection.py`
  - target: `models/detection/shared/evidence.py`
- `models/detection/typescript_detection.py`
  - target: `models/detection/typescript/discovery.py`
- `models/detection/typescript_rules.py`
  - split target:
    - TypeScript-only pieces -> `models/detection/typescript/rules.py`
    - generic rule primitives -> `models/detection/shared/rules.py`
- `models/configuration/settings.py`
  - move out:
    - `FileNode` -> `models/detection/shared/inventory.py`
    - `Signature`, `ManagerRule`, `LanguageRules` -> `models/detection/shared/rules.py`
    - `CodebaseDetection` -> either delete if unused or move into `models/detection/shared/results.py`

## Parser

- `parser/package_manager/package_manager_parser.py`
  - target: `parser/package_manager/shared/parser.py`
- `parser/package_manager/package_manager_factory.py`
  - target: `parser/package_manager/shared/registry.py`
- `parser/package_manager/package_manager_strategy.py`
  - target: `parser/package_manager/shared/strategy.py`
- `parser/package_manager/detectors/git_utils.py`
  - target: `parser/package_manager/shared/git_utils.py`
- `parser/package_manager/detectors/ripgrep_utils.py`
  - split target:
    - generic ripgrep wrappers -> `parser/package_manager/shared/ripgrep.py`
    - `find_python_mains` -> Python namespace
    - `parse_package_json_dependencies` -> TypeScript namespace
- `parser/package_manager/detectors/python_ripgrep_detector.py`
  - target: `parser/package_manager/python/detectors/ripgrep_detector.py`
- `parser/package_manager/detectors/typescript_ripgrep_detector.py`
  - target: `parser/package_manager/typescript/detectors/ripgrep_detector.py`
- `parser/package_manager/detectors/typescript_monorepo_detection_adapter.py`
  - target: `parser/package_manager/typescript/detectors/monorepo_detection_adapter.py`
- `parser/package_manager/detectors/typescript_standalone_detection_adapter.py`
  - target: `parser/package_manager/typescript/detectors/standalone_detection_adapter.py`
- `parser/package_manager/detectors/typescript_detection_utils.py`
  - target: `parser/package_manager/typescript/detectors/workspace_utils.py`
- `parser/package_manager/detectors/typescript_rules_loader.py`
  - target: `parser/package_manager/typescript/detectors/rules_loader.py`
- `parser/package_manager/node/node_package_manager_strategy.py`
  - target: `parser/package_manager/typescript/managers/package_json_strategy.py`
- `parser/package_manager/node/package_json_loader.py`
  - target: `parser/package_manager/typescript/manifests/package_json_loader.py`
- `parser/package_manager/pip/pip_strategy.py`
  - target: `parser/package_manager/python/managers/pip_strategy.py`
- `parser/package_manager/poetry/poetry_strategy.py`
  - target: `parser/package_manager/python/managers/poetry_strategy.py`
- `parser/package_manager/uv/uv_strategy.py`
  - target: `parser/package_manager/python/managers/uv_strategy.py`
- `parser/package_manager/utils/setup_parser.py`
  - target: `parser/package_manager/python/manifests/setup_parser.py`
- `parser/package_manager/utils/requirements_utils.py`
  - target: `parser/package_manager/python/manifests/requirements_loader.py`

# Compatibility strategy

## Rule

For the first migration pass, do not delete old modules immediately after moving code.

Instead:
1. Create the new target module.
2. Move the implementation into the new target module.
3. Replace the old module with a compatibility re-export shim.
4. Update imports across the codebase.
5. Run verification.
6. Remove the shim only after all imports and tests are green.

## Shim style

A shim module should do only one job: re-export the new canonical symbols. Do not keep logic split across old and new files.

Example pattern:

```python
from src.code_confluence_flow_bridge.models.detection.shared.results import (
    DetectedCodebase,
)
```

If a file is being renamed as part of a cleanup, prefer to keep the old class name temporarily and defer semantic renames until after the move lands cleanly.

# Naming guidance

- Prefer `shared`, `python`, and `typescript` package names.
- Prefer responsibility-oriented filenames inside each namespace:
  - `discovery.py`
  - `rules.py`
  - `manifests/...`
  - `managers/...`
- Avoid keeping `node/` as a top-level parser namespace because the current product language split is `python` and `typescript`.
- Avoid leaving detection primitives in `settings.py`; they are not environment/configuration settings.

# Recommended implementation phases

## Phase 1 - Establish namespaces and shared homes

Purpose: create the destination structure and move the safest shared primitives first.

Steps:
1. Create `models/detection/shared`, `models/detection/python`, and `models/detection/typescript` packages.
2. Create `parser/package_manager/shared`, `parser/package_manager/python`, and `parser/package_manager/typescript` packages.
3. Move `FileNode`, `Signature`, `ManagerRule`, and `LanguageRules` into shared detection modules.
4. Add compatibility shims in old locations.
5. Update the lowest-risk imports first.

Exit criteria:
- New packages exist.
- Shared primitives load from canonical shared modules.
- Old import paths still work through re-exports.

## Phase 2 - Move detection models and rules

Purpose: make `models/detection` follow the language-first design.

Steps:
1. Move TypeScript-specific models from flat files into `models/detection/typescript/`.
2. Split generic rule primitives from TypeScript-only rule wrappers.
3. Decide whether `CodebaseDetection` is still used; remove it if dead, otherwise move it into shared results.
4. Update imports in detector modules and tests.
5. Keep class names stable during this phase unless a rename is required to avoid collisions.

Exit criteria:
- No TypeScript-only model lives in the flat `models/detection/` root.
- `models/configuration/settings.py` no longer owns detection-specific models.

## Phase 3 - Move parser/package-manager code into language namespaces

Purpose: align parser structure with the same language-first boundaries.

Steps:
1. Move shared parser seams (`PackageManagerParser`, strategy interface, registry/factory, generic git/ripgrep helpers) into `parser/package_manager/shared/`.
2. Move Python detectors, managers, and manifest helpers into `parser/package_manager/python/`.
3. Move TypeScript detectors, package-json strategy, and package-json loader into `parser/package_manager/typescript/`.
4. Split `ripgrep_utils.py` so only generic ripgrep wrappers stay shared.
5. Update factory/registry imports after new canonical locations exist.

Exit criteria:
- `node/`, `pip/`, `poetry/`, and `uv/` are no longer the canonical homes.
- Shared parser root is thin and language-agnostic.

## Phase 4 - Unify rules loading and tighten type ownership

Purpose: remove duplicated structural patterns and make the layout internally consistent.

Steps:
1. Add a typed Python rules loader so Python and TypeScript use the same high-level pattern.
2. Move manifest helper models into language namespaces where it improves clarity.
3. Replace remaining generic stringly-typed package-manager evidence fields with stricter models only if the migration is already green.
4. Remove compatibility shims that no longer have import consumers.

Exit criteria:
- Python and TypeScript detection/rules loading follow the same architecture.
- Temporary compatibility modules are gone or clearly marked for a final cleanup task.

# Suggested PR boundaries

A junior developer should not try to land the whole reorganization in one PR.

Recommended PR sequence:
1. Shared namespaces + compatibility shims.
2. Detection-model relocation.
3. Parser/package-manager relocation.
4. Cleanup, dead imports, and shim removal.

# Implementation guardrails

- Do not mix structural moves with behavioral detector changes unless unavoidable.
- Do not rename classes and move files in the same step when a simple move is enough.
- Update one subsystem at a time and run verification after each subsystem.
- If a moved file is imported widely, convert call sites immediately after adding the shim so the shim is short-lived.
- Prefer absolute imports throughout.

# Verification checklist

Run after each phase that changes imports or module locations:

1. Type check first.

```bash
uv run --group dev basedpyright src/
```

2. Lint second.

```bash
uv run ruff check src/
```

3. Run targeted package-manager tests.

```bash
uv run --group test pytest tests/parser/package_manager/detectors/test_typescript_ripgrep_detector.py -v
```

4. Run any Python package-manager tests touched by the move.
5. If factories or workflow handoff code changed, run the closest targeted ingestion/package-metadata tests.

# Risks and watchouts

## High risk

- Moving `FileNode`, `Signature`, `ManagerRule`, and `LanguageRules` out of `settings.py` touches many imports.
- `PackageManagerStrategyFactory` is a central seam; moving it too early without shims will cause widespread breakage.
- `ripgrep_utils.py` currently mixes shared, Python-specific, and TypeScript-specific helpers.

## Medium risk

- `node_package_manager_strategy.py` is named after the ecosystem, but the current product language boundary is `typescript`; keep naming aligned with product language for now.
- Python currently hand-parses rules while TypeScript uses typed models; partial migration can leave asymmetry unless Phase 4 is completed.

## Low risk

- Creating new package directories and adding re-export shims.
- Moving TypeScript-only models into a `typescript/` package once imports are updated.

# Out of scope for this initiative

- Adding new package managers or languages.
- Changing detection algorithms as a primary goal.
- Changing stored metadata contracts unless required to preserve imports after the move.
- Renaming `typescript` to `node` or `javascript`.

# Definition of success

A new developer should be able to navigate directly to:
- `models/detection/python/...` for Python detection types
- `models/detection/typescript/...` for TypeScript detection types
- `parser/package_manager/python/...` for Python package-manager parsing
- `parser/package_manager/typescript/...` for TypeScript/package.json parsing
- `shared/...` locations for the small set of truly shared abstractions

without needing to discover language-specific logic in flat roots like `models/detection/`, `parser/package_manager/node/`, or `models/configuration/settings.py`.
