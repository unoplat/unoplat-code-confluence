---
id: TASK-16.9.1
title: >-
  Reframe TypeScript monorepo detection around workspace ownership and
  CLI-assisted project discovery
status: In Progress
assignee:
  - OpenCode
created_date: '2026-03-23 10:47'
updated_date: '2026-03-24 11:09'
labels:
  - backend
  - typescript
  - monorepo
  - ingestion
  - query-engine
  - workflow
  - task-16
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/typescript_ripgrep_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/detectors/ordered_detection.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/package_manager/detectors/test_typescript_ripgrep_detector.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/engineering_workflow_service.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/repository_metadata_service.py
  - research_npm_workspace_discovery.md
  - research_pnpm_workspace_discovery.md
  - research_turborepo_workspace_discovery.md
  - research_nx_workspace_discovery.md
  - validation_npm_query_workspace.md
  - validation_pnpm_list_recursive_json.md
  - validation_yarn_classic_workspaces_info_json.md
  - validation_yarn_berry_workspaces_list_json.md
  - validation_bun_workspace_resolution.md
parent_task_id: TASK-16.9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace the current leaf-first ordered package-manager detection approach for TypeScript monorepos with a workspace-aware strategy that separates workspace discovery, package-manager ownership, and workflow command discovery. The new approach should rely on authoritative workspace metadata and runner/package-manager CLIs where they add precision, while preserving deterministic fallbacks when those CLIs are unavailable in ingestion environments.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 TypeScript monorepo detection no longer uses generic ordered leaf re-detection to infer workspace member ownership when authoritative workspace context exists.
- [ ] #2 Workspace member enumeration has a documented precedence strategy covering config-file parsing and supported CLI discovery for npm, pnpm, Yarn, Turbo, and Nx, including behavior when a CLI is unavailable.
- [x] #3 Package-manager provenance for each workspace member is derived from explicit local ownership signals such as local lockfiles or packageManager fields, otherwise inherited from the nearest workspace owner.
- [x] #4 Stored metadata is sufficient for workflow generation to distinguish workspace runner commands from leaf-local package scripts without guessing standalone npm commands for inherited workspaces.
- [x] #5 Regression coverage proves inherited Bun/Turbo workspaces, nested workspace owners, and explicit child-local overrides behave correctly, and logs make workspace ownership decisions observable.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Adopt an orchestrator-first, adapter-based Python implementation for TypeScript monorepo discovery and ownership. Preserve single-responsibility boundaries first; extract shared utilities only after the adapter responsibilities are proven by implementation.

Implementation sequence:
1. Detect workspace orchestrator context first.
   - Identify repo-local orchestrator signals such as `turbo.json`/`turbo.jsonc` and `nx.json`/`project.json`/`workspace.json`.
   - Treat orchestrator detection as the entrypoint that decides which adapter stack should run.
2. Define narrow adapter contracts before extracting helpers.
   - Package-manager workspace adapters own workspace root discovery, member enumeration, and nearest-owner resolution.
   - Orchestrator adapters own orchestrator-specific metadata enrichment only.
   - Keep ownership resolution and runner metadata separate so each adapter has one responsibility.
3. Implement package-manager adapters as the authoritative topology layer.
   - npm/Yarn/Bun adapter: parse `package.json.workspaces`, preserve npm-like negation and ordering semantics where needed, and resolve ownership for npm-style workspaces.
   - pnpm adapter: parse `pnpm-workspace.yaml`, preserve mixed-pattern behavior and root probing, and resolve ownership for pnpm workspaces.
4. Implement orchestrator adapters as overlays on top of package-manager topology.
   - Turborepo adapter: detect repo/root context, reuse package-manager workspace membership, and attach `turbo.json`/`turbo.jsonc` task metadata without reproducing the full Turbo engine.
   - Nx adapter: detect Nx workspace/project context, reuse package-manager membership where applicable, and merge static `nx.json`/`project.json`/package `nx` metadata without executing plugins or building the full project graph.
5. After the first adapters exist, extract common utilities from repeated mechanics only.
   - Candidate shared utilities: manifest readers (JSON/YAML), path normalization, deterministic sorting, diagnostics/log helpers, and shared result models.
   - Do not prematurely generalize adapter-specific behaviors such as npm negation semantics, pnpm pattern handling, Nx merge rules, or Turbo config loading.
6. Introduce a single ownership resolver after adapter outputs are available.
   - Ownership precedence should be: explicit local ownership signal first, deepest containing workspace root second, inherited package-manager provenance last.
   - This resolver becomes the only place that decides final package-manager ownership for detected codebases.
7. Refactor the existing TypeScript detector flow to consume adapter outputs.
   - Move `typescript_ripgrep_detector.py` away from leaf-first generic re-detection.
   - Keep `ordered_detection.py` only for explicit local fallback signals where still needed.
8. Add tests in implementation order.
   - Adapter unit tests first.
   - Ownership-precedence tests second.
   - End-to-end detector regressions last, including inherited Bun/Turbo workspaces, nested workspace owners, pnpm exclusions, Nx/Turbo metadata overlays, and explicit child-local overrides.

Explicit scope boundaries:
- No CLI execution, VM execution, sandboxing, or plugin execution for this task.
- No attempt to reproduce full Turbo task-graph semantics or Nx project-graph/plugin behavior.
- Shared utility extraction happens after adapter responsibilities stabilize, not before.

Approved refinement: preserve the current ordered-detection/standalone behavior for non-monorepo TypeScript projects so existing single-package detection does not regress. Apply the new workspace-aware strategy only when authoritative monorepo/workspace context exists (workspace config or orchestrator metadata that resolves members/ownership). In practice: non-monorepo paths continue to use the current local detector flow; monorepo paths must prefer authoritative workspace discovery, explicit local ownership signals, nearest-owner inheritance, and orchestrator overlays instead of generic leaf-first re-detection.

Validated against the upstream reference notes captured in the repo: for this iteration, optimize around the real-world single-root workspace model used by npm, pnpm, Yarn, Turbo, and Nx. Do not make recursive child `package.json.workspaces` scanning a primary discovery path. Keep compatibility-safe behavior where it already exists, but treat authoritative monorepo discovery as root-owned workspace metadata plus explicit child-local ownership overrides rather than nested workspace roots.

User approved the detector simplification refactor after review. Implementation plan for this pass: (1) extract detection/workspace/rules Pydantic models from `typescript_ripgrep_detector.py` and `ordered_detection.py` into dedicated model modules under `src/code_confluence_flow_bridge/models/`; (2) introduce `typescript_detection_utils.py` for pure reusable TypeScript workspace/path helpers such as normalization, rebasing, segment matching, glob expansion, nearest-owner lookup, and child-of checks; (3) simplify `ManagerDetectionResult` into a lean evidence model and move construction branching into detector logic; (4) split TypeScript detection flow by responsibility so workspace-aware monorepo resolution is isolated from standalone/local ordered detection while preserving the existing fast ripgrep scan; (5) keep performance stable by retaining single-scan inventory/caches and only moving pure logic behind clearer seams; (6) update detector regressions to cover refactored utilities/behavior and reduce the oversized test file where practical; (7) verify with basedpyright first, then ruff, then targeted pytest per repo conventions.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Launched parallel DeepWiki-based subagent research for npm, pnpm, Turborepo, and Nx to support an adapter-based Python implementation with no CLI/VM dependency. Findings converge on a hybrid static-parser architecture: package-manager adapters own workspace membership and nearest-owner resolution; Turborepo/Nx adapters add repo-local runner/project metadata without reimplementing full graph/execution engines.

Validated the root research notes for npm, pnpm, Turborepo, and Nx against DeepWiki MCP plus upstream GitHub source using four parallel research subagents. All four notes need correction before being treated as implementation-grounding documents.

npm: keep @npmcli/map-workspaces as the authority, but correct the mapWorkspaces signature/options, glob-vs-minimatch roles, negation semantics, duplicate tracking, and folder-name fallback when package name is missing.

pnpm: keep findWorkspaceDir/readWorkspaceManifest/findWorkspaceProjectsNoCheck as the authority, but correct the default pattern behavior when packages is absent, exact manifest read/error semantics, and make sure root inclusion plus mixed-pattern tinyglobby behavior are preserved.

Turborepo: keep package-manager detection + repo inference + turbo-json loader references, but correct the claim that Turbo delegates discovery entirely, fix bun/yarn/pipeline/dual-config behaviors, and treat the Python sketch as materially misleading unless rewritten as an approximation.

Nx: keep plugin-based discovery and package-manager workspace extraction, but correct nx.json/workspace-root assumptions, project.json/package.json merge precedence, target inference details, root-project behavior, and workspace.json legacy wording.

Rewrote the root research notes for npm, pnpm, Turborepo, and Nx into shorter upstream-grounded references with explicit source files, corrected discovery algorithms, edge cases, and implementation guidance.

Added separate CLI-focused validation notes for `npm query .workspace`, `pnpm list --depth -1 -r --json`, Yarn Classic `yarn workspaces info --json`, Yarn Berry `yarn workspaces list --json`, and Bun workspace resolution. These notes capture command-specific output behavior, precise upstream file/function refs, and approximation-only Python sketches.

Ran a second validation round after the rewrites. Current status: `research_npm_workspace_discovery.md`, `research_pnpm_workspace_discovery.md`, `research_turborepo_workspace_discovery.md`, and `research_nx_workspace_discovery.md` all validate as aligned against DeepWiki-guided official GitHub source after minor wording fixes.

User-approved implementation order for TASK-16.9.1: detect workspace orchestrator context first, implement adapter-based responsibilities around that orchestrator boundary to preserve SRP, then extract repeated mechanics into shared utilities only after the adapter shape is validated.

This means package-manager adapters will own workspace topology and nearest-owner resolution, orchestrator adapters will act as metadata overlays, and utility extraction is intentionally delayed until npm-like/pnpm/Turbo/Nx behaviors are concretely implemented and compared.

User approved proceeding with the explicit regression guardrail: keep current non-monorepo detection behavior unchanged, and apply the new authoritative strategy only for monorepo/workspace-aware cases.

User supplied additional upstream/ecosystem guidance: major orchestrators reject nested workspaces in practice, and real-world TypeScript monorepos converge on a single flat/root workspace definition. Implementation will therefore prioritize root-owned authoritative workspace discovery and explicit child-local overrides, while avoiding new complexity around recursive nested workspace scanning.

Implemented detector-side authoritative root workspace handling in `typescript_ripgrep_detector.py`: non-monorepo detection keeps the existing ordered-detector flow, while root-owned monorepos now resolve workspace membership from authoritative workspace config first and use explicit child-local ownership signals (`packageManager`, lockfiles/configs, `pnpm-workspace.yaml`) instead of generic leaf re-detection.

Added additive metadata for workflow generation in commons/detector persistence: `workspace_orchestrator` and `workspace_orchestrator_config_path` now round-trip through `ProgrammingLanguageMetadata`, `DetectedCodebase`, and `build_programming_language_metadata()` so inherited Turbo/Nx workspaces preserve runner context.

Preserved compatibility-safe nested workspace behavior without making it the primary discovery path: authoritative root workspaces remain primary, but nested compatibility workspaces still suppress aggregator leaves and now inherit root orchestrator metadata when discovered beneath an authoritative root.

Added regression coverage for inherited Bun/Turbo workspaces, pnpm root workspaces, explicit child-local overrides, nested compatibility workspace suppression, standalone non-monorepo behavior, and Nx root orchestrator metadata in `test_typescript_ripgrep_detector.py`.

Verification run: `uv run --group dev basedpyright src/code_confluence_flow_bridge/parser/package_manager/detectors/typescript_ripgrep_detector.py src/code_confluence_flow_bridge/parser/package_manager/detectors/ordered_detection.py src/code_confluence_flow_bridge/models/detection/detected_codebase.py src/code_confluence_flow_bridge/routers/repository/mappers.py tests/parser/package_manager/detectors/test_typescript_ripgrep_detector.py`; `uv run ruff check src/code_confluence_flow_bridge/parser/package_manager/detectors/typescript_ripgrep_detector.py src/code_confluence_flow_bridge/parser/package_manager/detectors/ordered_detection.py src/code_confluence_flow_bridge/models/detection/detected_codebase.py src/code_confluence_flow_bridge/routers/repository/mappers.py tests/parser/package_manager/detectors/test_typescript_ripgrep_detector.py`; `uv run --group test pytest tests/parser/package_manager/detectors/test_typescript_ripgrep_detector.py -v`.

Starting approved simplification pass focused on maintainability/readability without changing intended TypeScript detector behavior.
<!-- SECTION:NOTES:END -->
