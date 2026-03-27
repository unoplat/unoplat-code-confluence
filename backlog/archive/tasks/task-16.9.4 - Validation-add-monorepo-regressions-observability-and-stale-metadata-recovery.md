---
id: TASK-16.9.4
title: >-
  Validation: add monorepo regressions, observability, and stale-metadata
  recovery
status: To Do
assignee: []
created_date: '2026-03-23 07:06'
updated_date: '2026-03-23 07:10'
labels:
  - backend
  - typescript
  - monorepo
  - tests
  - observability
  - bug
  - task-16
dependencies:
  - TASK-16.9.1
  - TASK-16.9.2
  - TASK-16.9.3
  - TASK-16.9.5
references:
  - unoplat-code-confluence-query-engine/t3code-logfire-investigation-report.md
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/package_manager/detectors/test_typescript_ripgrep_detector.py
  - unoplat-code-confluence-query-engine/tests
  - unoplat-code-confluence-commons/tests
parent_task_id: TASK-16.9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add cross-package regressions, Logfire-backed diagnostics, and a recovery path for already-ingested repositories whose stored metadata still marks inherited workspaces as local npm projects.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Cross-package regression coverage verifies mixed-manager TypeScript monorepo metadata round-tripping and catches inherited-workspace package-manager regressions.
- [ ] #2 Logfire-backed diagnostics make stale or malformed TypeScript monorepo metadata observable during workflow generation and metadata derivation failures.
- [ ] #3 Already-ingested repositories with stale metadata that incorrectly marks inherited workspaces as local npm projects follow a documented and test-covered recovery path that restores correct workspace ownership semantics.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add missing regression suites across commons, ingestion, and query-engine for metadata round-tripping and workspace-aware workflow generation.
2. Add targeted diagnostics so prompt metadata source conflicts are visible in runtime traces.
3. Define a recovery path for repositories already ingested with stale monorepo metadata, including re-ingestion or backfill expectations.
4. Use t3code as the primary canary fixture for validation before and after fixes.
<!-- SECTION:PLAN:END -->
