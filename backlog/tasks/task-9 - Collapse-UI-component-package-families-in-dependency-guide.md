---
id: TASK-9
title: Collapse UI component package families in dependency guide
status: Done
assignee:
  - OpenCode
created_date: '2026-03-08 05:24'
updated_date: '2026-03-10 09:31'
labels:
  - dependency-guide
  - frontend
  - cost-optimization
  - workflow
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/dependency_guide_fetch_activity.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_dependency_repository.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/event_stream_handler.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/statistics_helpers.py
  - >-
    unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts
  - unoplat-code-confluence-frontend/src/lib/agent-md-to-markdown.ts
documentation:
  - >-
    https://logfire-us.pydantic.dev/jayghiya/unoplat-code-confluence?q=trace_id%3D%27019cc6b086da24fda466c36da3475f50%27
priority: high
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reduce redundant dependency-guide agent work for frontend codebases by collapsing component-level UI packages into canonical library families before documentation generation. This should cut repeated web-search/model/event overhead for suites like `@radix-ui/react-*`, keep the first rollout backward compatible for existing dependency-guide consumers, and make it easy to add more UI library families over time.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Configured UI component library families defined in an external JSON registry produce one canonical dependency-guide entry per configured family instead of one entry per component package.
- [ ] #2 Dependencies that do not match an explicit configured UI family rule, including unconfigured scoped families such as `@tanstack/*`, continue to generate deterministic per-package dependency-guide entries.
- [ ] #3 The first rollout keeps the existing dependency-guide output contract backward compatible for current snapshot/frontend consumers.
- [ ] #4 UI library family coverage is driven solely by explicit external JSON configuration rather than generic namespace/scope deduplication or hard-coded workflow branches.
- [ ] #5 Tests cover registry-driven family matching, deduplication within configured UI families only, stable ordering, and the workflow fan-out reduction to one dependency-guide run per normalized family target.
- [ ] #6 Task notes document the Onyx/Logfire motivation, the chosen insertion point, the explicit JSON-controlled family filter requirement, and follow-up opportunities intentionally left out of the first rollout.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Preserve the current raw dependency source.
- Keep `fetch_codebase_dependencies(...)` as the repository-level source of truth for raw runtime package names from the `default` dependency group.
- Do not move UI-family grouping into the PostgreSQL repository in the first rollout.

2. Introduce a pure UI component library normalization layer before dependency-guide fan-out.
- Add a small, deterministic normalization module in query-engine that converts raw package names into documentation targets only when they match explicit UI component library rules.
- Drive matching from an external JSON registry file instead of hard-coded workflow branches.
- Support exact-name, prefix, and regex-style matchers in that JSON so new UI component library families can be added by editing the file rather than rewriting orchestration logic.
- Scope the first rollout to frontend ecosystems only (TypeScript/JavaScript package families) to avoid accidental grouping of backend/runtime packages.

3. Make the external JSON registry the sole control surface for grouping.
- Only dependencies that match an enabled JSON rule should collapse into a canonical documentation target.
- Do not apply generic dedupe by scope, namespace, prefix, or naming convention outside those explicit rules.
- Families such as `@tanstack/*` must remain one-package-per-entry unless they are intentionally added to the JSON registry later.

4. Normalize to canonical documentation targets while keeping output backward compatible.
- Internal normalized target shape should capture at least: canonical/display name, optional search query override, matched source packages, and optional language/package-manager scope.
- The workflow should continue producing the existing `DependencyGuideEntry` output shape (`name`, `purpose`, `usage`) for the first rollout.
- Do not add new frontend snapshot/schema fields in the first pass unless strictly necessary.

5. Update dependency-guide workflow fan-out.
- After raw dependency fetch, normalize/dedupe/stably order documentation targets.
- Run the dependency-guide agent once per normalized target instead of once per raw package.
- For grouped UI families, pass the canonical family/library name into the dependency-guide prompt so the existing output contract remains valid.
- Preserve one-to-one behavior for unmatched dependencies and all non-configured families.

6. Ensure deterministic behavior and clear rule precedence.
- Define precedence rules for overlapping matchers (for example: exact > prefix > regex, or explicit registry order if that is simpler to reason about).
- Guarantee stable ordering so repeated runs do not reshuffle dependency-guide output when the underlying dependency set is unchanged.
- Dedupe multiple raw packages only when they map to the same configured UI family before any LLM calls occur.

7. Add tests around registry-driven normalization and workflow behavior.
- Unit tests for matcher behavior, precedence, dedupe, and stable ordering.
- Tests that configured `@radix-ui/react-*` packages collapse to one normalized target.
- Tests that unconfigured families such as `@tanstack/*` continue through unchanged as separate dependency-guide targets.
- Workflow-level tests that grouped UI families reduce dependency-guide fan-out to one agent run per normalized target.
- If practical in touched scope, assert that stats aggregation now reflects normalized runs rather than per-component-package runs.

8. Keep adjacent follow-ups documented but out of scope for the first rollout.
- Optional future enhancement: include `source_packages` provenance in stored dependency-guide output and UI rendering.
- Optional future enhancement: broaden JSON registry coverage to more frontend ecosystems/library families.
- Adjacent issue noticed during investigation: `INTERNAL_DEPENDENCY_SKIP` appears defined in the dependency-guide prompt path, but downstream filtering was not found during code reading; treat this as a separate follow-up unless it becomes necessary while implementing TASK-9.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Current end-to-end behavior:
- Raw runtime package names are fetched from PostgreSQL in `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_dependency_repository.py`.
- `DependencyGuideFetchActivity` currently acts as a pass-through and returns a plain `list[str]` of dependency names from `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/dependency_guide_fetch_activity.py`.
- `temporal_workflows.py` then iterates that list sequentially and runs `dependency_guide` once per dependency.
- The dependency-guide agent prompt in `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py` is explicitly written for a single library/package at a time.
- The first-pass output contract is currently `DependencyGuideEntry(name, purpose, usage)` in `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py`.
- Frontend snapshot parsing/rendering currently assumes exactly that shape in `unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts` and `unoplat-code-confluence-frontend/src/lib/agent-md-to-markdown.ts`.

Observed problem / motivation:
- Frontend UI ecosystems often publish many component packages under one documentation family, for example `@radix-ui/react-dialog`, `@radix-ui/react-popover`, and `@radix-ui/react-tabs`.
- The current one-package-per-run behavior causes repeated tool/model work even though those packages should usually resolve to one family-level documentation description.
- This amplifies token usage, tool activity, event-stream persistence, and workflow duration for dependency-guide runs.

Onyx / Logfire evidence from the reported run:
- Investigated trace: `019cc6b086da24fda466c36da3475f50`.
- Logfire link is attached in task documentation.
- Read-only Logfire queries during investigation showed `84` `dependency_guide run` entries on that trace.
- The same trace showed `300` `RunActivity:agent__dependency_guide__model_request_stream` records.
- The same trace showed `223` dependency-guide tool-call activity records.
- The same trace showed `439` dependency-guide event-stream handler start/run activity records.
- Interpretation: dependency-guide fan-out is currently large enough that repetitive family-level docs become expensive in both tokens and stored event volume.

Insertion points considered:
1. PostgreSQL repository layer.
- Pros: earliest possible normalization point.
- Cons: mixes storage access with product-specific documentation grouping semantics.
- Decision: not preferred for first rollout.

2. Fetch activity / service boundary after raw dependency fetch and before workflow fan-out.
- Pros: deterministic, early enough to eliminate redundant LLM/event work, keeps repository focused on raw data access, and is reusable for future dependency-guide consumers.
- Cons: requires changing the activity/output shape or adding normalization adjacent to the activity path.
- Decision: preferred seam for first rollout.

3. Workflow-only normalization directly inside `temporal_workflows.py`.
- Pros: small local change.
- Cons: embeds registry/normalization policy inside orchestration and is less reusable/testable.
- Decision: acceptable fallback, but not the recommended design.

4. Render-only/frontend-only grouping.
- Pros: simplest presentation change.
- Cons: does not reduce tokens, model calls, tool calls, or persisted event volume; only hides the symptom.
- Decision: explicitly rejected for this task.

Recommended design direction:
- Keep raw dependency fetch unchanged.
- Add a pure dependency-family registry/normalizer that converts raw package names into canonical documentation targets.
- Registry entries should be data-driven and extensible. Useful fields:
  - canonical display/documentation name
  - match rules (exact / prefix / regex)
  - optional search query override for official docs lookup
  - matched raw `source_packages`
  - optional language / package-manager constraints
- First rollout should target TypeScript/JavaScript frontend UI package families only.
- Example family rule: prefix `@radix-ui/react-` => canonical family such as `Radix UI React Primitives`.
- Future families can later include libraries like MUI, Chakra UI, Headless UI, Mantine, and Ant Design, but they do not all need to ship in the first change.

Backward compatibility decision for first rollout:
- Keep `DependencyGuideEntry` unchanged.
- Keep frontend snapshot schema/rendering unchanged.
- Grouping should happen before the dependency-guide agent is invoked; the agent should simply receive the canonical family/library name as its input.
- If provenance is later needed in UI/docs, a follow-up can add `source_packages` or similar metadata to output models and frontend rendering.

Behavioral expectations for normalization:
- Unmatched dependencies remain one-to-one and should behave exactly as today.
- Multiple raw packages that map to one family should dedupe before any dependency-guide agent run occurs.
- Matching precedence must be deterministic and documented.
- Output ordering must remain stable across runs for the same dependency set.

Testing focus:
- Unit coverage for rule matching, precedence, dedupe, and stable ordering.
- Workflow coverage that many raw Radix packages produce one dependency-guide agent run and one resulting entry.
- Backward-compatibility coverage that existing consumers still accept the resulting payload shape.

Known adjacent follow-up to capture separately if needed:
- `INTERNAL_DEPENDENCY_SKIP` is defined in the dependency-guide agent path, but downstream filtering was not located during investigation. This is worth a separate cleanup unless implementation of TASK-9 naturally touches that branch.

2026-03-08: User clarified that grouping must be opt-in and limited to UI component library families explicitly listed in an external JSON registry. No generic namespace/scope dedupe is allowed. Unconfigured families such as `@tanstack/*` must remain separate dependency-guide entries by default.

2026-03-08: Implemented the first pass of registry-driven UI family grouping in query-engine. Added `DependencyGuideTarget` runtime models, a pure normalization service, and an external JSON registry at `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/config/ui_component_dependency_families.json`.

2026-03-08: Updated `DependencyGuideFetchActivity` to normalize raw dependency names into dependency-guide targets using programming-language and package-manager scope, and updated `temporal_workflows.py` to fan out one dependency-guide run per normalized target rather than per raw package. Unmatched dependencies still pass through one-to-one.

2026-03-08: Added targeted tests covering configured Radix family collapsing, unconfigured `@tanstack/*` pass-through, deterministic dedupe/ordering, language scoping, and dependency-guide prompt enrichment. Validation run results: touched-file basedpyright passed; touched-file ruff check passed; targeted pytest passed (7 tests). Repo-wide basedpyright still has many unrelated pre-existing errors outside TASK-9 scope.

2026-03-08: Inspected Onyx web dependencies at `/Users/jayghiya/Documents/unoplat/onyx/web/package.json` to look for additional UI component library families beyond Radix. Confirmed heavy `@radix-ui/react-*` usage and found `@dnd-kit/*` (`core`, `modifiers`, `sortable`, `utilities`) as another multi-package UI library family suitable for explicit registry grouping. Left single-package libraries such as `@headlessui/react` unchanged.

2026-03-08: Extended the external UI family registry with a `@dnd-kit/` prefix rule mapped to canonical library `dnd kit` and added targeted test coverage to confirm configured dnd-kit packages collapse while unconfigured families like `@tanstack/*` still remain separate. Validation rerun after the registry update: touched-file basedpyright passed, touched-file ruff check passed, dependency-guide normalization pytest passed (6 tests).
<!-- SECTION:NOTES:END -->
