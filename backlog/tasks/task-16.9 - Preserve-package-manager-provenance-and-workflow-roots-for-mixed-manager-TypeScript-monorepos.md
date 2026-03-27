---
id: TASK-16.9
title: >-
  Preserve package-manager provenance and workflow roots for mixed-manager
  TypeScript monorepos
status: To Do
assignee: []
created_date: '2026-03-21 06:37'
updated_date: '2026-03-23 10:47'
labels:
  - backend
  - typescript
  - monorepo
  - schema
  - query-engine
  - bug
  - agent-skills
  - alpha
  - task-16
dependencies:
  - TASK-16.8
references:
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/programming_language_metadata.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/configuration_models.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/typescript_ripgrep_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/repository/mappers.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/repository_ruleset_metadata.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/engineering_workflow_output.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/agents/code_confluence_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/engineering_workflow_service.py
documentation:
  - 'https://bun.sh/docs/pm/workspaces'
  - 'https://pnpm.io/workspaces'
  - 'https://pnpm.io/pnpm-workspace_yaml'
  - 'https://ai.pydantic.dev/toolsets/#agent-skills'
  - 'https://ai.pydantic.dev/api/toolsets/'
  - 'https://agentskills.io/specification'
  - 'https://dougtrajano.github.io/pydantic-ai-skills/'
parent_task_id: TASK-16
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Mixed-manager TypeScript monorepos currently collapse package-manager identity down to a single effective value, so downstream workflow generation cannot tell whether a manager was detected locally or inherited from a parent workspace, nor which directory actually owns the package-manager/workspace commands. In layouts such as a Bun root containing a nested pnpm workspace, this causes engineering workflow guidance to inspect and recommend commands from the wrong scope. Add end-to-end metadata support so detected codebases preserve package-manager provenance and execution-root context, and update workflow generation to use that context when producing reviewable commands for alpha codebase configuration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Saved codebase metadata for TypeScript monorepos distinguishes the effective package manager from its provenance and nearest workspace root so downstream consumers can tell whether a manager is local to the codebase or inherited from a parent workspace.
- [ ] #2 Mixed-manager nested monorepo detection emits correct package-manager provenance and workspace-root metadata for representative layouts, including child-local manager override when a workspace member owns a stronger local manager than its parent aggregator.
- [ ] #3 Engineering workflow output includes a repo-relative `working_directory` whose semantics are unambiguous (`None`/omitted = codebase root, `.` = repository root, nested path = workspace root), with raw-output validation rejecting invalid values and normalization preserving the distinction for valid ones.
- [ ] #4 The development workflow agent receives monorepo-aware relative and absolute workspace-root context and can load a dedicated TypeScript monorepo skill through PydanticAI toolsets so workflow guidance stays concise by default but expands for monorepo-specific caveats when needed.
- [ ] #5 Regression coverage across commons, flow-bridge, and query-engine verifies metadata round-tripping, mixed-manager detection, working-directory normalization, and monorepo prompt/skill behavior for nested workspaces.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Prepare local cross-package development wiring before implementation. `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/pyproject.toml` and `unoplat-code-confluence-query-engine/pyproject.toml` currently resolve `unoplat-code-confluence-commons` from the remote git source, so switch those `tool.uv.sources` entries to the local checkout during implementation/testing (or otherwise ensure the local commons checkout is the installed source) before relying on consumer type checks or tests.

2. Extend the shared commons metadata schema in `unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/programming_language_metadata.py`. Add a `PackageManagerProvenance` enum with `local` and `inherited`, then add optional `package_manager_provenance` and `workspace_root` fields to `ProgrammingLanguageMetadata`. Keep these fields additive and optional so existing Python and standalone codebases remain backward-compatible. Update the relevant package exports in `unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/__init__.py` and `unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/__init__.py`.

3. Refactor the Flow Bridge TypeScript detector so effective manager resolution is correct before codebase emission. Introduce a structured detection payload (for example `DetectedCodebase`) carrying `manager_name`, `provenance`, and `workspace_root`. Implement the detection algorithm in this order inside `_fast_detect()`:
   a. Keep the existing directory inventory pass (`dirs_to_files`, `known_dirs_list`, `workspace_member_dirs`, `workspace_excluded_dirs`, `aggregator_manager_map`, `done_dirs`) so the traversal order remains shallow-to-deep.
   b. In Branch A (`directory_path in workspace_member_dirs`), first confirm the directory is TypeScript with `_is_typescript_project()`.
   c. Resolve inherited context with `_find_aggregator_manager()`, which must now return the deepest matching `(manager_name, aggregator_dir)` tuple rather than only the manager string.
   d. Re-detect the current directory's local manager before inheriting by calling `ordered_detector.detect_manager(directory_path, files_in_dir, repo_path)` using the directory's own files from `dirs_to_files`. Treat local detection as authoritative when it returns a manager, including cases where the child manager differs from the inherited parent manager.
   e. Choose effective ownership with these exact rules: if `local_manager` is present, set `effective_manager=local_manager`, `effective_provenance=PackageManagerProvenance.LOCAL`, and `effective_workspace_root=None`; otherwise set `effective_manager=inherited_manager`, `effective_provenance=PackageManagerProvenance.INHERITED`, and `effective_workspace_root=aggregator_dir`.
   f. Resolve nested workspace membership for the effective manager by calling `_resolve_workspace_glob_sets(directory_path, repo_path, effective_manager, known_dirs_list)`. This must use the effective manager so a child-local pnpm workspace can read `pnpm-workspace.yaml` instead of incorrectly inheriting Bun workspace parsing.
   g. If nested members are found, suppress the current directory as an aggregator, register the resolved nested members/exclusions, and write `aggregator_manager_map[directory_path] = effective_manager` so descendants inherit from the nearest owner. If no nested members are found, emit `DetectedCodebase(manager_name=effective_manager, provenance=effective_provenance, workspace_root=effective_workspace_root)` and mark the directory done.
   h. In Branch B (normal detection), keep standalone behavior but emit `DetectedCodebase(..., provenance=LOCAL, workspace_root=None)` for non-aggregator TypeScript codebases.
   i. Preserve existing nested suppression rules and pnpm workspace-glob support; if child-local pnpm detection currently depends on `pnpm-workspace.yaml` recognition from `TASK-16.8`, verify that dependency first so this task does not silently regress mixed-manager layouts.

4. Update Flow Bridge workspace ownership helpers to preserve nearest-owner semantics. Change `_find_aggregator_manager()` to sort aggregators deepest-first and return both the manager and the owning aggregator directory. Keep `workspace_root` defined as the nearest directory that owns workspace/package-manager commands for the emitted leaf: `None` for standalone or locally owned leaf codebases, `.` for repo-root workspace ownership, and a nested repo-relative path such as `packages/platform` for nested workspace ownership. Preserve the existing nested aggregator suppression logic while moving it to the new structured detection flow.

5. Update Flow Bridge codebase-config construction and metadata reconstruction to round-trip the new fields. Change the TypeScript detector's `_build_codebase_config()` to accept the structured detection result and populate `package_manager_provenance` plus `workspace_root` in `ProgrammingLanguageMetadata`. Update `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/repository/mappers.py` so `build_programming_language_metadata()` reconstructs those optional fields from stored JSONB metadata without breaking older rows.

6. Extend query-engine repository metadata with both relative and absolute workspace context. In `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/repository_ruleset_metadata.py`, add optional fields for `codebase_package_manager_provenance`, `codebase_workspace_root`, and derived absolute `codebase_workspace_root_path`. Implement the metadata derivation algorithm in `repository_metadata_service.py` as follows:
   a. Continue resolving `absolute_path` from `CodebasePathResolver`, but treat it as potentially missing or non-absolute because the current service already falls back to repo-relative paths when resolution fails.
   b. Read `raw_plm = config.programming_language_metadata` from JSONB and extract `package_manager_provenance` / `workspace_root` only when the stored values are strings; otherwise leave them `None`.
   c. Normalize `relative_path` and `workspace_root` as repo-relative POSIX values conceptually, but do not mutate persisted metadata in this service; this layer only derives runtime fields for the agent.
   d. Derive `repo_root_path` only when `absolute_path` is an absolute filesystem path. Use `pathlib.Path` / `PurePosixPath` rather than string slicing: if `relative_path == "."`, then `repo_root_path = Path(absolute_path)`; otherwise compute the number of segments in `PurePosixPath(relative_path).parts` and walk up that many parents from `Path(absolute_path)`.
   e. If `absolute_path` is missing or not absolute, leave `codebase_workspace_root_path=None` and log a warning instead of synthesizing an invalid path.
   f. If `workspace_root` is `None`, set `codebase_workspace_root_path=None`. If `workspace_root == "."`, set `codebase_workspace_root_path` to `str(repo_root_path)`. Otherwise join `repo_root_path` with `PurePosixPath(workspace_root)` and serialize the result as a string.
   g. Only populate the absolute workspace-root field when both `repo_root_path` and `workspace_root` are valid; malformed or escaping values should fail closed to `None` rather than leaking invalid runtime paths into agent dependencies.
   h. Keep `ProgrammingLanguageMetadataOutput` and the separate package-metadata query path unchanged unless targeted tests prove they also need the new fields.

7. Add `working_directory` to engineering-workflow output with explicit semantics. Update `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/engineering_workflow_output.py` and `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/engineering_workflow_service.py` so `working_directory` means: omitted/`None` = run from the codebase root, `.` = run from the repository root, any other repo-relative POSIX path = run from a specific workspace root. Implement `_normalize_working_directory()` so it preserves `.`, rejects absolute or escaping paths, falls back safely for malformed persisted data, and participates in command deduplication. Update `validate_engineering_development_workflow_output()` in `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py` so invalid raw model output is rejected before normalization.

8. Update the development-workflow prompt so monorepo context is explicit but still minimal. In `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/agents/code_confluence_agents.py`, include package-manager provenance, repo-relative `workspace_root`, and absolute `workspace_root_path` when present. Add a short monorepo hint that tells the agent to use the TypeScript monorepo skill and, when command scope differs from the leaf root, inspect workspace-level configuration from `workspace_root_path` via `get_directory_tree` / `read_file_content`. Keep detailed command-selection rules out of the base prompt; the base prompt should only define the `working_directory` contract and when to consult the skill.

9. Integrate a dedicated TypeScript monorepo skill through PydanticAI toolsets in query-engine. Add `pydantic-ai-skills` to `unoplat-code-confluence-query-engine/pyproject.toml`, create a programmatic `typescript-monorepo` skill that captures workspace command guidance (install/build/test/lint/type-check scope, inherited-manager caveats, `working_directory` rules), and attach it to the development-workflow agent only for monorepo-relevant runs. Before coding, confirm the exact `Skill`/`SkillsToolset` import path and dynamic toolset registration API against the installed `pydantic-ai` / `pydantic-ai-skills` version so the implementation follows the documented API instead of assuming an unsupported decorator shape. Configure Temporal activity settings for the additional skill toolset id.

10. Add regression coverage across all three packages. Commons: schema round-trip and backward-compat tests. Flow Bridge: update existing TypeScript detector fixtures to assert provenance/workspace-root fields; add a mixed-manager Bun-root -> nested pnpm workspace regression and a local-manager leaf regression that proves child-local re-detection wins over inherited manager. Query-engine: add tests for workspace metadata derivation, `working_directory` normalization (`None` vs `.` vs nested path), deduplication, prompt text that includes only a minimal monorepo hint plus workspace context, and conditional skill loading/instruction injection.

11. Verify in package-specific order, running type checks before lint where tooling exists. Commons: targeted `uv run pytest tests/test_programming_language_metadata.py -v`. Flow Bridge: targeted `uv run --group dev basedpyright ...`, then `uv run ruff check ...`, then targeted `uv run --group test pytest ...`. Query-engine: targeted `uv run --group dev basedpyright ...`, then `uv run ruff check ...`, then targeted `uv run --group test pytest ...`. Expand to broader suites only when targeted verification exposes package-level regressions.

Execute remaining work in category order: ingestion detection/persistence -> ingestion workflow propagation -> query-engine metadata reconciliation -> workspace-aware workflow generation -> cross-package validation and stale-metadata recovery.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Review corrections incorporated into the implementation plan: child-local manager re-detection is required before inherited-manager fallback; prompt/runtime metadata must include workspace-root context; `working_directory` semantics must distinguish codebase root (`None`) from repository root (`.`); and cross-package verification must use the local commons checkout instead of the currently pinned remote git source.

Subtask breakdown captured for remaining bug work: `TASK-16.9.1` detector/persistence metadata, `TASK-16.9.3` ingestion workflow propagation, `TASK-16.9.5` query-engine metadata source-of-truth and consistency guards, `TASK-16.9.2` workspace-aware Turbo/Nx workflow generation, and `TASK-16.9.4` regressions/observability/backfill.

Archived the earlier subtask split (`TASK-16.9.1` through `TASK-16.9.5`) and replaced it with a single fresh subtask, `TASK-16.9.1`, centered on a revised strategy: separate workspace discovery, ownership resolution, and workflow command discovery; evaluate config parsing versus CLI-assisted project enumeration for npm/pnpm/Yarn/Turbo/Nx instead of continuing the previous leaf-first ordered-detector decomposition.
<!-- SECTION:NOTES:END -->
