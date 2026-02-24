---
id: AGENT-1
title: >-
  Move dependency overview to separate markdown artifact and update section
  updater behavior
status: In Progress
assignee:
  - OpenCode
created_date: '2026-02-24 11:39'
updated_date: '2026-02-24 12:08'
labels:
  - agents-md
  - dependency-guide
  - documentation
  - temporal
dependencies: []
references:
  - AGENTS.md
  - CLAUDE.md
  - dependencies_overview.md
  - >-
    src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
documentation:
  - 'backlog://workflow/overview'
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Objective
Move verbose dependency details out of AGENTS.md into a dedicated markdown artifact while preserving a concise Dependency Guide section in AGENTS.md.

Why
Keeping dependency details inline in AGENTS.md makes the file harder to scan and causes generated updates to keep expanding that section. A dedicated artifact improves readability and keeps generated outputs structured.

Proposed changes
1) Create a new artifact file `dependencies_overview.md` at repository root containing dependency overview entries.
2) Update `AGENTS.md` so `## Dependency Guide` no longer stores full dependency entries and instead points to `dependencies_overview.md`.
3) Update `CLAUDE.md` agent-context sentence so dependency guidance points to the new artifact file.
4) Update Temporal section-updater configuration so dependency-guide updater run manages both `AGENTS.md` and `dependencies_overview.md` going forward.
5) Keep section heading/order semantics intact (`## Dependency Guide` remains section 2 in AGENTS.md order).

Scope notes
- No change to dependency extraction logic itself.
- No change to dependency agent output schema.
- Business-domain and app-interface companion artifacts remain as-is.

Planned code/files
Create:
- `dependencies_overview.md`

Modify:
- `AGENTS.md`
- `CLAUDE.md`
- `src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py` (dependency section artifact mapping + updater instructions)

Validation strategy
- Run `task typecheck` first.
- Run `task lint` second.
- Confirm updater prompt artifact list for dependency section includes `dependencies_overview.md`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `dependencies_overview.md` exists at repository root and contains the dependency overview content.
- [x] #2 `AGENTS.md` keeps a `## Dependency Guide` section that references `dependencies_overview.md` instead of embedding full dependency details.
- [x] #3 `CLAUDE.md` agent-context text references the dependency artifact location correctly.
- [x] #4 Dependency section updater configuration includes `dependencies_overview.md` as a managed artifact alongside `AGENTS.md`.
- [ ] #5 Typecheck and lint pass after the change set (`task typecheck` then `task lint`).
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create `dependencies_overview.md` in `unoplat-code-confluence-query-engine` and move the existing dependency entries from AGENTS into this file.
2. Update `AGENTS.md` `## Dependency Guide` to a concise index section that points to `dependencies_overview.md` (no full dependency catalog inline).
3. Update `CLAUDE.md` agent-context sentence to mention `dependencies_overview.md` for dependency details.
4. Update `src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py` so dependency section updater artifacts include `dependencies_overview.md` alongside `AGENTS.md`.
5. Add explicit dependency-section-specific prompt guidance in `build_section_updater_prompt` to keep AGENTS concise and place full dependency details in `dependencies_overview.md`.
6. Run validation in required order: `task typecheck` first, then `task lint`.
7. If checks fail, apply focused fixes and re-run until passing or report any unrelated pre-existing blockers with details.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented artifact split: created `unoplat-code-confluence-query-engine/dependencies_overview.md` and migrated full dependency entries there.

Updated `unoplat-code-confluence-query-engine/AGENTS.md` Dependency Guide section to concise pointer text referencing `dependencies_overview.md`.

Updated `unoplat-code-confluence-query-engine/CLAUDE.md` agent-context sentence to point dependency details to `dependencies_overview.md`.

Updated dependency section updater behavior in `src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py`: `SECTION_ARTIFACTS[SectionId.DEPENDENCY_GUIDE]` now includes `dependencies_overview.md`, plus section-specific prompt requirements to keep AGENTS concise and place full catalog in the dependency artifact.

Validation run order executed as requested: `task typecheck` then `task lint`.

Both full-repo checks failed due pre-existing unrelated issues in other modules; no new errors reported in modified file when running targeted checks: `uv run --group dev basedpyright src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py` and `uv run --group dev ruff check src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py` (both pass).
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Migration keeps AGENTS.md concise without removing dependency guide discoverability.
- [ ] #2 No behavior regressions for business_domain/app_interfaces artifact handling.
<!-- DOD:END -->
