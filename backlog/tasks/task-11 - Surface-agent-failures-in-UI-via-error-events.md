---
id: TASK-11
title: Surface agent failures in UI via error events
status: To Do
assignee: []
created_date: '2026-03-08 14:33'
updated_date: '2026-03-19 09:57'
labels:
  - bug
  - full-stack
  - agent-events
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/engineering_workflow_completion_activity.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_worker_manager.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/tracking/repository_agent_snapshot_service.py
  - unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts
  - unoplat-code-confluence-frontend/src/types/agent-events.ts
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentGroupHeader.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventItem.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsProgressLive.tsx
  - unoplat-code-confluence-frontend/src/components/ui/badge.tsx
priority: high
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Problem

When a backend agent fails (e.g., `business_domain_agents_md_updater` fails with `AgentExecutionError: Tool 'updater_apply_patch' exceeded max retries count of 2`), the UI incorrectly shows the agent group as "COMPLETED". The bottom bar shows "Failed" but individual agent groups all display green checkmarks.

**Screenshot evidence**: All 4 agent groups show "COMPLETED" with green checkmarks even though `business_domain_agents_md_updater` failed during the run.

### Root Cause (3-layer gap)

1. **Backend gap**: Error handlers in `temporal_workflows.py` collect errors in-memory (`agent_errors` list) but never persist them as events to the `repository_agent_event` table. The `_map_event_to_phase()` in `event_stream_handler.py` only maps 3 PydanticAI stream events: `FunctionToolCallEvent → "tool.call"`, `FunctionToolResultEvent → "tool.result"`, `FinalResultEvent → "result"`.

2. **Frontend status gap**: `getAgentStatus()` in `agent-events-utils.ts` only knows 3 states: `pending | running | completed`. Status is determined solely by presence of `phase === "result"` event — no error/failed concept exists.

3. **Aliased child failure masking**: The parent guide (e.g., `business_domain_guide`) emits its own `"result"` phase event before the child updater (`business_domain_agents_md_updater`) fails. Since the updater's failure is never persisted as an event, the frontend only sees the parent's "result" event and reports "COMPLETED".

### Approach

Emit `phase="error"` events from backend error handlers → frontend detects and displays "FAILED" status with error precedence over "completed".

**Note**: The `phase` column is `Mapped[str]` (plain string, no check constraint) in the DB model and `z.string()` in the frontend schema. Electric SQL syncs new phase values automatically. No migration needed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 When a backend agent fails, a `phase="error"` event is persisted to `repository_agent_event` table with the failing agent name and a truncated error message
- [ ] #2 The frontend `getAgentStatus()` returns `"error"` when any event in the group has `phase === "error"`, with error taking precedence over completed
- [ ] #3 Agent groups with errors display a red XCircle icon, "FAILED" badge (using existing `error` badge variant), and destructive styling
- [ ] #4 The summary text includes failed count (e.g., "2 completed · 1 failed")
- [ ] #5 Error events from aliased agents (e.g., `business_domain_agents_md_updater`) are correctly grouped into their parent agent group via existing `AGENT_ALIASES`
- [ ] #6 Error event emission failures do not break the workflow's resilience strategy (wrapped in try/except)
- [ ] #7 Existing runs without error events continue to work unchanged (backward compatible)
<!-- AC:END -->
