---
id: TASK-16.9.3
title: Make query-engine monorepo metadata loading authoritative and self-consistent
status: To Do
assignee: []
created_date: '2026-03-23 11:13'
updated_date: '2026-03-23 11:14'
labels:
  - backend
  - typescript
  - monorepo
  - query-engine
  - bug
  - task-16
dependencies:
  - TASK-16.9.1
  - TASK-16.9.2
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/repository_metadata_service.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_package_metadata_repository.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/package_manager_metadata_service.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/repository_ruleset_metadata.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/agents/code_confluence_agents.py
  - unoplat-code-confluence-query-engine/t3code-logfire-investigation-report.md
parent_task_id: TASK-16.9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make query-engine metadata derivation use a single authoritative view of TypeScript monorepo ownership so prompt assembly cannot mix effective package manager data from one source with provenance or workspace-root data from another. This task includes source-consistency guards, diagnostics, and the t3code reproduction path for the npm/local mismatch observed in workflow prompts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Query-engine metadata loading derives package_manager, package_manager_provenance, workspace_root, and related workspace context from an authoritative and internally consistent source model.
- [ ] #2 If stored metadata and package metadata disagree about monorepo ownership, query-engine diagnostics make the disagreement observable and fail closed or reconcile deterministically instead of emitting contradictory prompt context.
- [ ] #3 The t3code reproduction path no longer produces npm/local metadata at prompt-construction time when the stored workspace metadata indicates inherited Bun workspace ownership.
- [ ] #4 Regression coverage verifies metadata derivation, conflict handling, and prompt-construction behavior for inherited workspaces and stale/contradictory metadata cases.
<!-- AC:END -->
