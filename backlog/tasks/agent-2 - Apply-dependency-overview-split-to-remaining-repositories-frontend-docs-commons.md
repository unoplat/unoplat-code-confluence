---
id: AGENT-2
title: >-
  Apply dependency overview split to remaining repositories (frontend, docs,
  commons)
status: Done
assignee:
  - OpenCode
created_date: '2026-02-24 12:10'
updated_date: '2026-02-24 12:20'
labels:
  - agents-md
  - dependency-guide
  - documentation
dependencies:
  - AGENT-1
references:
  - unoplat-code-confluence-frontend/AGENTS.md
  - unoplat-code-confluence-frontend/CLAUDE.md
  - unoplat-code-confluence-docs/AGENTS.md
  - unoplat-code-confluence-docs/CLAUDE.md
  - unoplat-code-confluence-commons/AGENTS.md
documentation:
  - 'backlog://workflow/overview'
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Objective
Apply the same dependency-guide split pattern used in query-engine to the remaining repositories in this workspace by moving inline dependency details from AGENTS.md to a dedicated `dependencies_overview.md` artifact.

Repositories in scope
- unoplat-code-confluence-frontend
- unoplat-code-confluence-docs
- unoplat-code-confluence-commons

Planned changes per repository
1) Create `<repo>/dependencies_overview.md` with the current dependency catalog from `<repo>/AGENTS.md`.
2) Update `<repo>/AGENTS.md` `## Dependency Guide` to a concise pointer to `dependencies_overview.md`.
3) Update `<repo>/CLAUDE.md` Agent Context references to dependency guidance in `dependencies_overview.md` where CLAUDE.md exists.

Scope notes
- Manual docs-only updates right now (no generator/temporal code changes in these repositories).
- For `unoplat-code-confluence-commons`, only AGENTS.md + dependencies_overview.md are in scope because no CLAUDE.md exists.
- Keep existing section ordering and all non-dependency sections unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `unoplat-code-confluence-frontend/dependencies_overview.md` exists and contains frontend dependency details migrated from AGENTS.md.
- [x] #2 `unoplat-code-confluence-docs/dependencies_overview.md` exists and contains docs dependency details migrated from AGENTS.md.
- [x] #3 `unoplat-code-confluence-commons/dependencies_overview.md` exists and contains commons dependency details migrated from AGENTS.md.
- [x] #4 Each in-scope AGENTS.md keeps a concise `## Dependency Guide` section that points to `dependencies_overview.md` rather than embedding full dependency entries.
- [x] #5 `unoplat-code-confluence-frontend/CLAUDE.md` and `unoplat-code-confluence-docs/CLAUDE.md` Agent Context text references `dependencies_overview.md` for dependency details.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. For each in-scope repository (frontend, docs, commons), extract the current inline `## Dependency Guide` content from `AGENTS.md`.
2. Create `<repo>/dependencies_overview.md` and place the extracted dependency content there, preserving existing wording.
3. Replace each `AGENTS.md` dependency section body with concise pointer bullets referencing `dependencies_overview.md`.
4. Update Agent Context lines in `unoplat-code-confluence-frontend/CLAUDE.md` and `unoplat-code-confluence-docs/CLAUDE.md` so dependency details are sourced from `dependencies_overview.md`.
5. Verify diffs only touch the intended markdown files and no unrelated sections changed.
6. Update backlog acceptance criteria and notes with completion status and file list.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created dependency artifacts: `unoplat-code-confluence-frontend/dependencies_overview.md`, `unoplat-code-confluence-docs/dependencies_overview.md`, and `unoplat-code-confluence-commons/dependencies_overview.md` with migrated dependency catalogs from each AGENTS.md.

Updated dependency sections in `unoplat-code-confluence-frontend/AGENTS.md`, `unoplat-code-confluence-docs/AGENTS.md`, and `unoplat-code-confluence-commons/AGENTS.md` to concise pointer format referencing `dependencies_overview.md`.

Updated Agent Context dependency references in `unoplat-code-confluence-frontend/CLAUDE.md` and `unoplat-code-confluence-docs/CLAUDE.md` to point to `dependencies_overview.md`.

Confirmed all `unoplat-code-confluence-*/AGENTS.md` dependency sections now use concise overview pointer style and all in-scope repositories have a `dependencies_overview.md` artifact.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Manually applied the dependency-guide split pattern across the remaining repositories (frontend, docs, commons). Each repository now stores detailed dependency content in a dedicated `dependencies_overview.md`, while `AGENTS.md` keeps a concise `## Dependency Guide` pointer section. CLAUDE agent-context references were updated in frontend and docs repositories to direct dependency details to `dependencies_overview.md`.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 No unrelated content changes outside dependency guide references and new dependency artifact files.
- [x] #2 All created/updated markdown files are readable and use consistent heading/link style.
<!-- DOD:END -->
