---
id: TASK-16.9.4
title: Generate Turbo and Nx workflows from authoritative workspace metadata
status: To Do
assignee: []
created_date: '2026-03-23 11:13'
updated_date: '2026-03-23 11:14'
labels:
  - backend
  - typescript
  - monorepo
  - query-engine
  - workflow
  - task-16
dependencies:
  - TASK-16.9.1
  - TASK-16.9.3
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/engineering_workflow_service.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/engineering_workflow_output.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/agents/code_confluence_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/skills/typescript-monorepo/SKILL.md
parent_task_id: TASK-16.9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once ingestion and query-engine metadata are trustworthy, make engineering workflow generation favor authoritative workspace-runner behavior for Turbo and Nx monorepos. The goal is to emit reviewable commands that preserve runner ownership, correct working-directory semantics, and leaf-local script references without guessing standalone npm flows for inherited workspaces.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Engineering workflow generation prefers authoritative Turbo and Nx runner commands when workspace metadata indicates the workspace runner owns build, test, lint, or typecheck flows.
- [ ] #2 Workflow output distinguishes repository-root runner commands from leaf-local package scripts using unambiguous working-directory semantics.
- [ ] #3 Prompt or skill context tells the agent when to inspect workspace-runner metadata and when to reference leaf-local scripts, without falling back to guessed standalone npm commands for inherited workspaces.
- [ ] #4 Regression coverage verifies Turbo and Nx workspace cases, including at least one inherited workspace where root runner commands and leaf-local scripts are both present but the runner remains authoritative.
<!-- AC:END -->
