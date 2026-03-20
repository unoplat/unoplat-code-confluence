---
id: TASK-11.2
title: 'Frontend: Display error status for failed agent groups'
status: To Do
assignee: []
created_date: '2026-03-08 14:34'
updated_date: '2026-03-19 09:57'
labels:
  - frontend
  - agent-events
  - ui
dependencies:
  - TASK-11.1
references:
  - unoplat-code-confluence-frontend/src/types/agent-events.ts
  - unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentGroupHeader.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventItem.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsProgressLive.tsx
  - unoplat-code-confluence-frontend/src/components/ui/badge.tsx
parent_task_id: TASK-11
priority: high
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context

This is the frontend half of TASK-11 (Surface agent failures in UI via error events). Depends on TASK-11.1 which emits `phase="error"` events from the backend. The frontend currently only knows 3 agent statuses (`pending | running | completed`) and determines "completed" by looking for a `phase === "result"` event. It has no concept of error/failed status.

**Note**: `getAgentStatus()` was recently modified to accept an `isCompleted?: boolean` parameter. The error status must take precedence over both this external completion signal and the `phase === "result"` check.

## What to build

### 1. Widen status type to include `"error"`

**File**: `src/types/agent-events.ts` (line 10)

Change `status: "pending" | "running" | "completed"` to `status: "pending" | "running" | "completed" | "error"`.

### 2. Update `getAgentStatus` with error precedence

**File**: `src/lib/agent-events-utils.ts`

Change return type to include `"error"`. Add error check as the **highest precedence** — before the `isCompleted` check and before the `"result"` phase check:

```typescript
const hasErrorPhase = events.some((event) => event.phase === "error");
if (hasErrorPhase) {
  return "error";
}
```

**Why error overrides completed**: The parent guide (e.g., `business_domain_guide`) may emit `"result"` before its child updater (`business_domain_agents_md_updater`) fails. The error event from the updater is aliased into the same group. Error must win.

### 3. Add `failed` to `AgentGroupSummaryCounts`

**File**: `src/lib/agent-events-utils.ts`

- Add `failed: number` to `AgentGroupSummaryCounts` interface
- Add `group.status === "error"` branch in `getAgentGroupSummaryCounts` that increments `failed`

### 4. Error rendering in `AgentGroupHeader`

**File**: `src/components/custom/agent-events/AgentGroupHeader.tsx`

- Import `XCircle` from `lucide-react`
- `getStatusIcon`: add `if (status === "error")` returning `<XCircle className="h-4 w-4 shrink-0 text-destructive" />`
- `getStatusVariant`: return `"error"` — this badge variant already exists in `badge.tsx` (line 31-32: `bg-destructive/10 text-destructive`)
- `getStatusLabel`: return `"FAILED"`
- Widen return types of all 3 helper functions to include the new values

### 5. Error phase in `AgentEventItem`

**File**: `src/components/custom/agent-events/AgentEventItem.tsx`

- Import `XCircle` from `lucide-react`
- Add `"error"` to the `PhaseType` union type (line 9)
- Add entry to `PHASE_CONFIG` (line 16): `error: { icon: XCircle, iconClassName: "text-destructive" }`

### 6. Summary text update

**File**: `src/components/custom/GenerateAgentsProgressLive.tsx`

In `getCodebaseAgentSummary()` (~line 138-157), add after the running check:
```typescript
if (summary.failed > 0) {
  parts.push(`${summary.failed} failed`);
}
```

## Existing utilities to reuse
- Badge `"error"` variant in `src/components/ui/badge.tsx` (line 31-32)
- `AGENT_ALIASES` in `agent-events-utils.ts` already maps updater agent names to parent groups
- `groupEventsByAgent()` already resolves aliases — error events with updater names will naturally land in the parent group

## Verification
1. `bunx tsc -b --pretty false` — typecheck
2. `bun eslint <each-modified-file>` — lint per file
3. `bun prettier --write <each-modified-file>` — format per file
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AgentGroup status type includes `"error"` alongside existing `pending | running | completed`
- [ ] #2 `getAgentStatus()` returns `"error"` when any event has `phase === "error"`, with error as highest precedence (above isCompleted and result phase)
- [ ] #3 AgentGroupHeader renders error status with red XCircle icon, `"error"` badge variant, and "FAILED" label
- [ ] #4 AgentEventItem renders error-phase events with red XCircle icon and `text-destructive` styling
- [ ] #5 AgentGroupSummaryCounts includes `failed` count and summary text displays it (e.g., "2 completed \u00b7 1 failed")
- [ ] #6 All existing statuses (pending, running, completed) continue to render correctly
- [ ] #7 tsc, eslint, and prettier pass cleanly on all modified files
<!-- AC:END -->
