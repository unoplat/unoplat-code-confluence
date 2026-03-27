---
id: TASK-16.9.5
title: >-
  Query engine metadata: use authoritative monorepo fields and add consistency
  guards
status: To Do
assignee: []
created_date: '2026-03-23 07:09'
updated_date: '2026-03-23 07:10'
labels:
  - backend
  - typescript
  - monorepo
  - query-engine
  - bug
  - task-16
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/repository_metadata_service.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_package_metadata_repository.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/package_manager_metadata_service.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/repository_ruleset_metadata.py
  - unoplat-code-confluence-query-engine/t3code-logfire-investigation-report.md
parent_task_id: TASK-16.9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make repository metadata loading treat stored codebase-config monorepo fields as the authoritative source for package_manager, package_manager_provenance, and workspace_root, reconcile conflicts with package metadata safely, and fail closed before prompt assembly when sources disagree.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Repository metadata loading uses stored codebase-config monorepo fields as the authoritative source for package_manager, package_manager_provenance, and workspace_root when building agent dependencies.
- [ ] #2 Conflicting package-manager values from separate metadata tables are reconciled deterministically or fail closed with diagnostic logging instead of silently producing contradictory prompt state.
- [ ] #3 Derived workspace_root_path is only populated for safe, valid repo-relative workspace roots and absolute codebase paths.
- [ ] #4 A regression reproducing the t3code mismatch proves the query-engine no longer passes `npm/local` prompt metadata for inherited Bun workspace members.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Audit every source that contributes package manager information to `CodebaseMetadata`.
2. Remove or constrain source-of-truth splitting between stored codebase config metadata and package metadata tables.
3. Add consistency guards and Logfire-visible warnings when upstream sources disagree.
4. Add tests covering inherited workspace metadata, malformed values, and the t3code mismatch scenario.
<!-- SECTION:PLAN:END -->
