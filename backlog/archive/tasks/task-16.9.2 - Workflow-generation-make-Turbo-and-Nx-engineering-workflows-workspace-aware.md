---
id: TASK-16.9.2
title: 'Workflow generation: make Turbo and Nx engineering workflows workspace-aware'
status: To Do
assignee: []
created_date: '2026-03-23 07:06'
updated_date: '2026-03-23 07:10'
labels:
  - backend
  - typescript
  - monorepo
  - query-engine
  - workflow
  - task-16
dependencies:
  - TASK-16.9.5
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/engineering_workflow_output.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/engineering_workflow_service.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/agents/code_confluence_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/skills/typescript-monorepo/SKILL.md
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/turbo_monorepo/t3code/package.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/turbo_monorepo/t3code/turbo.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/test_data/turbo_monorepo/t3code/AGENTS.md
parent_task_id: TASK-16.9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Improve development workflow generation for inherited TypeScript workspaces by passing explicit workspace and task-runner context into the agent and prioritizing workspace-owned Turbo/Nx commands over standalone npm-style guesses.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Development workflow agent input includes explicit workspace-root and task-runner context for TypeScript workspaces when available, including enough detail to distinguish repo-root execution from workspace-root execution.
- [ ] #2 Engineering workflow generation prefers workspace-owned Turbo and Nx commands when workspace metadata indicates those runners own the build/test/lint/type-check flow, instead of defaulting to standalone npm-style scripts from the leaf package.
- [ ] #3 Generated workflow output preserves correct working-directory semantics for workspace-owned commands and rejects invalid workspace-scoped command locations through existing raw-output validation or normalization tests.
- [ ] #4 Regression coverage verifies Turbo and Nx workspace scenarios for inherited TypeScript workspaces, including at least one case where the leaf package should not emit standalone npm-style guesses because the workspace runner is the authoritative entry point.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Enrich workflow agent context with authoritative workspace-root, package-manager provenance, task-runner, and package identity hints.
2. Bias command discovery toward root workspace scripts and Turbo/Nx task runners before falling back to leaf-local scripts.
3. Keep `working_directory` semantics strict so repo-root, workspace-root, and codebase-root execution remain distinct.
4. Extend the TypeScript monorepo skill so it reinforces workspace-owned command selection for inherited monorepos.
<!-- SECTION:PLAN:END -->
