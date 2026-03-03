---
id: TASK-4
title: Fix Live Tool Events Screen — Backend Clipping + Flow 1/Flow 2 Visual Overhaul
status: To Do
assignee: []
created_date: '2026-03-02 07:48'
updated_date: '2026-03-03 05:26'
labels:
  - frontend
  - backend
  - ux
  - electric-sql
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/events/agent_events.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/event_stream_handler.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/tracking/repository_agent_snapshot_service.py
  - >-
    unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts
  - unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts
  - unoplat-code-confluence-frontend/src/types/agent-events.ts
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventItem.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventsAccordion.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/ToolResultExpander.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/ToolDetailModal.tsx
    (new)
documentation:
  - >-
    Paper design file page tool-dialog-improvements: artboard 155-0 (Flow 1),
    artboard X6-0 (Flow 2), artboard V3-0 (defects annotated), artboard R7-0
    (current state)
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Problem

The Generate AGENTS.md dialog live tool events screen had three UX defects in Paper (`V3-0`):

1. CALL and RESULT rows were visually flat with weak pairing cues.
2. Inline `[more]` expansion clipped result content.
3. CALL and RESULT styling lacked strong differentiation for scanability.

Backend clipping and missing persisted tool metadata also prevented full-fidelity frontend rendering.

## Goal

Deliver the final Live Tool Events experience from Paper:
- **Flow 1** (`155-0`): improved accordion with explicit CALL/RESULT rows, connector rail, pending treatment, and `View details ->` CTA.
- **Flow 2** (`X6-0`): separate detail dialog opened from Flow 1 showing full args and full result content with copy actions.

## Agreed Constraints

- Tool result content capped at **100,000 chars** in backend persistence.
- Frontend CALL↔RESULT pairing is **strictly by `tool_call_id`**.
- **No FIFO fallback pairing path**.
- UI implementation is **shadcn-first** (reuse existing primitives where available).

## Active Subtasks

1. **TASK-4.1** (backend persistence) — completed.
2. **TASK-4.4** (frontend strict pairing + Flow 1 + Flow 2 + cleanup) — active.

`TASK-4.2` and `TASK-4.3` are superseded and archived to avoid conflicting requirements.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 TASK-4.1 and TASK-4.4 are completed.
- [ ] #2 Frontend event pairing is strict `tool_call_id` matching with no FIFO fallback code path.
- [ ] #3 Flow 1 accordion matches Paper `155-0` for completed and pending tool-pair rows.
- [ ] #4 Clicking `View details ->` opens Flow 2 as a separate dialog layer (not inline expansion).
- [ ] #5 Flow 2 dialog shows full formatted tool args and full tool result content with working copy actions.
- [ ] #6 Electric SQL-delivered frontend event objects include `tool_name`, `tool_call_id`, `tool_args`, and `tool_result_content`.
- [ ] #7 `ToolResultExpander.tsx` is removed and has no remaining import references.
- [ ] #8 Implementation reuses shadcn primitives where available and avoids duplicate custom primitives.
- [ ] #9 Backend and frontend quality checks pass (`basedpyright`/`ruff` for backend changes, `bun run lint` and `bun run build` for frontend changes).
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Keep backend scope in TASK-4.1 as the completed persistence foundation.
2. Execute frontend in TASK-4.4 as the single source of truth for schema, strict pairing, Flow 1, Flow 2, and cleanup.
3. Validate functional behavior and visual parity against Paper (`155-0`, `X6-0`).
4. Run project quality checks and finalize parent once subtask completion is confirmed.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Current Direction Alignment

- Backend scope (TASK-4.1) is complete and remains the persistence foundation.
- Frontend execution is consolidated into TASK-4.4 to avoid conflicting requirements.
- Archived tasks (`TASK-4.2`, `TASK-4.3`) are superseded and must not be used for implementation guidance.

## Pairing and UX Rules

- CALL↔RESULT pairing is strict by `tool_call_id`.
- No FIFO fallback pairing path.
- `View details ->` must open a separate Flow 2 dialog layer.
- shadcn-first component reuse is required where equivalent primitives exist.

## Validation Expectations

- Visual verification against Paper `155-0` and `X6-0` is required.
- Regression checks must include frontend lint/build and backend quality gates already run for TASK-4.1.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Parent acceptance criteria are all checked.
- [ ] #2 TASK-4.4 notes include visual validation against Paper `155-0` and `X6-0`.
- [ ] #3 No conflicting active subtasks remain for this parent.
- [ ] #4 Final parent summary records superseded subtasks and final implementation scope.
<!-- DOD:END -->
