---
id: TASK-4.2
title: >-
  Frontend: Extend Electric SQL Zod schema + update CALL↔RESULT pairing to use
  tool_call_id
status: To Do
assignee: []
created_date: '2026-03-02 08:01'
updated_date: '2026-03-02 08:07'
labels:
  - frontend
  - typescript
  - electric-sql
dependencies:
  - TASK-4.1
references:
  - >-
    unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts
  - unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts
  - unoplat-code-confluence-frontend/src/types/agent-events.ts
parent_task_id: TASK-4
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context

Once backend subtask (TASK-4.1) is done, new events will carry `tool_name`, `tool_call_id`, `tool_args`, and `tool_result_content` inside the JSONB `events` array. This subtask updates the frontend schema and pairing utility to consume those fields.

Electric SQL syncs the `repository_agent_md_snapshot` table rows; the `events` JSONB column is parsed by `repositoryAgentEventSchema` in `schema.ts`. The pairing logic in `buildEventDisplayItems()` currently uses FIFO array-position matching, which can mispair concurrent tool calls.

## What to Change

### File 1: `schema.ts`
Add four optional fields to `repositoryAgentEventSchema`:
```typescript
tool_name: z.string().optional().nullable(),
tool_call_id: z.string().optional().nullable(),
tool_args: z.record(z.unknown()).optional().nullable(),
tool_result_content: z.string().optional().nullable(),
```
All fields are `.optional().nullable()` for backward compat with pre-migration events.

### File 2: `agent-events-utils.ts`
Rewrite `buildEventDisplayItems()` with ID-based pairing while preserving FIFO fallback:

```
Algorithm:
1. Build callsById: Map<string, RepositoryAgentEvent> for call events that have tool_call_id
2. Build pendingFifoCalls: RepositoryAgentEvent[] for call events without tool_call_id (legacy)
3. Build resultsByCallId: Map<string, RepositoryAgentEvent> for result events that have tool_call_id
4. Emit output in original event order:
   - For a call event with tool_call_id: emit tool-pair { callEvent, resultEvent: resultsByCallId.get(tool_call_id) }
   - For a call event without tool_call_id: use FIFO queue to pair with next result-without-tool_call_id
   - Skip result events that were already consumed (paired by ID or FIFO)
   - Emit remaining unpaired events as single items
```

Do NOT change `groupEventsByAgent`, `getAgentStatus`, `truncateMessage`, `AgentType`, or `AGENT_ALIASES`.

### File 3: `types/agent-events.ts`
Add new exported interfaces:
```typescript
export interface ToolDetailItem {
  callEvent?: RepositoryAgentEvent;
  resultEvent?: RepositoryAgentEvent;
}

export interface ToolDetailModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  item: ToolDetailItem | null;
}
```

Update `AgentEventItemProps`:
```typescript
onViewDetails?: (item: ToolDetailItem) => void;
```

## Key Technical Notes

- `z.record(z.unknown())` is the correct Zod type for `tool_args` (TypeScript: `Record<string, unknown>`)
- No `any` types anywhere (CLAUDE.md constraint)
- `buildEventDisplayItems()` must handle the case where a result arrives before its call in the array (edge case — emit result as single item)
- All imports must be top-level absolute imports (CLAUDE.md constraint)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 repositoryAgentEventSchema has tool_name, tool_call_id, tool_args (z.record), tool_result_content fields (all optional/nullable)
- [ ] #2 RepositoryAgentEvent TypeScript type inferred from schema includes the four new fields
- [ ] #3 buildEventDisplayItems() pairs CALL+RESULT by tool_call_id when both have tool_call_id
- [ ] #4 buildEventDisplayItems() falls back to FIFO queue for events without tool_call_id
- [ ] #5 ToolDetailItem and ToolDetailModalProps interfaces exported from types/agent-events.ts
- [ ] #6 AgentEventItemProps includes onViewDetails?: (item: ToolDetailItem) => void
- [ ] #7 bun tsc --noEmit: 0 errors
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 bun tsc --noEmit returns 0 errors
- [ ] #2 All acceptance criteria checked
- [ ] #3 Final summary written
<!-- DOD:END -->
