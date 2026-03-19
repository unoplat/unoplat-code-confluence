---
id: TASK-12.1
title: Prevent duplicate AGENTS.md run starts for same repository
status: To Do
assignee: []
created_date: '2026-03-10 11:03'
updated_date: '2026-03-19 09:57'
labels:
  - frontend
  - ux
  - operations-management
  - agent-md
  - workflow-concurrency
dependencies: []
references:
  - >-
    unoplat-code-confluence-frontend/src/components/custom/IngestedRepositoriesDataTable.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsDialog.tsx
  - unoplat-code-confluence-frontend/src/lib/api.ts
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py
parent_task_id: TASK-12
priority: high
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Operations UX should prevent users from starting multiple AGENTS.md generation/update runs for the same repository at the same time. Current behavior can trigger multiple concurrent repository agent workflows, which creates ambiguity for cancellation/status targeting and noisy operations history.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 When a repository already has an in-flight AGENTS_GENERATION or AGENT_MD_UPDATE run, UI blocks starting another run for that same repository.
- [ ] #2 Start/Generate CTA shows clear disabled state and explanatory copy while a run is active.
- [ ] #3 Operations and repository status views stay consistent after refresh; no duplicate in-flight starts can be initiated via normal UI flow.
- [ ] #4 User can start a new AGENTS.md run again once previous run reaches terminal status.
- [ ] #5 Manual QA steps are documented for active-run, terminal-run, and refresh/navigation scenarios.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Frontend behavior includes optimistic guard + server state recheck before start action
- [ ] #2 No regression for ingestion operation flows
<!-- DOD:END -->
