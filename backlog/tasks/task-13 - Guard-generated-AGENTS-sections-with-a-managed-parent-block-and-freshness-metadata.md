---
id: TASK-13
title: >-
  Guard generated AGENTS sections with a managed parent block and freshness
  metadata
status: In Progress
assignee: []
created_date: '2026-03-12 13:34'
updated_date: '2026-03-12 13:38'
labels:
  - agents-md
  - query-engine
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py
priority: high
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a single guarded parent block in generated codebase-local AGENTS.md content so all agent-managed sections live inside one deterministic container. Capture the repository default-branch commit used for generation and expose that freshness metadata once inside the managed block, instead of duplicating commit notes across Engineering Workflow, Dependency Guide, Business Logic Domain, and App Interfaces sections.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Generated codebase-local AGENTS.md content is wrapped in a single guarded parent block with explicit start/end markers and CRITICAL_INSTRUCTION tags.
- [ ] #2 All section updater runs operate only inside the managed parent block and preserve deterministic section ordering within that block.
- [ ] #3 Repository default branch name and head commit SHA are resolved once per repository workflow run and made available to the parent-block freshness metadata.
- [ ] #4 Freshness metadata appears once in the managed block and covers Engineering Workflow, Dependency Guide, Business Logic Domain, and App Interfaces without duplicating commit notes inside individual sections.
- [ ] #5 The existing manual PR publication flow continues to detect changed files from updater_runs and publishes the resulting AGENTS.md/artifact diffs correctly.
- [ ] #6 Tests cover prompt generation, managed-block bootstrapping/finalization behavior, and shared GitHub ref resolution logic.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Introduce a shared repository git-ref resolver that fetches the default branch and its current head SHA via GitHub API, then reuse that logic from both the generation workflow path and the manual PR publication endpoint to avoid duplicate branch/SHA lookup code.

2. Add a workflow-level step before subsection updater runs that resolves freshness metadata once per repository workflow run and passes the resulting default_branch/commit_sha payload into downstream codebase workflows.

3. Add a parent managed-block lifecycle for codebase-local AGENTS.md generation:
- bootstrap or normalize the guarded CODEBASE AGENT RULES block before section-specific updater runs begin;
- keep all generated sections inside that guarded block;
- finalize the single freshness statement inside the same block after section content has been updated.

4. Extend the section-updater prompt/model wiring so subsection writers are scoped to the managed parent block rather than the whole AGENTS.md file. Update section-order instructions so Engineering Workflow, Dependency Guide, Business Logic Domain, and App Interfaces are treated as children of the guarded block, and ensure their prompts explicitly avoid duplicating freshness notes.

5. Add explicit prompt/template support for the managed freshness statement so it references the resolved default branch and commit SHA once and clearly states that the generated sections may become stale as new commits land.

6. Preserve existing updater run recording and manual PR publication behavior by keeping the parent-block bootstrap/finalization steps represented in updater run metadata, so changed-file detection continues to work from agents_md_updater_runs.file_changes.

7. Add or update tests for:
- shared GitHub ref resolution behavior;
- prompt construction and section ordering within the managed block;
- parent-block bootstrap/finalization behavior;
- compatibility of changed-file collection / PR publication with the new managed-block flow.

8. Validate the implementation with repository-standard checks in the preferred order: typecheck first, then lint, then targeted pytest coverage for the affected workflow/updater modules.
<!-- SECTION:PLAN:END -->
