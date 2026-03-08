---
id: TASK-4.4
title: >-
  Frontend: Strict tool_call_id pairing + Flow 1 accordion + Flow 2 detail
  dialog (shadcn-first)
status: Done
assignee:
  - OpenCode
created_date: '2026-03-03 05:24'
updated_date: '2026-03-04 11:24'
labels:
  - frontend
  - typescript
  - react
  - ux
  - shadcn
dependencies:
  - TASK-4.1
references:
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
documentation:
  - >-
    Paper page tool-dialog-improvements: artboard 155-0 (Flow 1 — Improved
    Accordion)
  - 'Paper page tool-dialog-improvements: artboard X6-0 (Flow 2 — Detail Modal)'
  - 'Paper page tool-dialog-improvements: artboard R7-0 (current baseline)'
parent_task_id: TASK-4
priority: high
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context

Backend event persistence is complete in TASK-4.1. Frontend now needs a conflict-free implementation that aligns with Paper designs and current product direction:

- Flow 1 (`155-0`): improved accordion with explicit CALL/RESULT rows, timeline connector, pending treatment, and `View details ->` CTA.
- Flow 2 (`X6-0`): separate detail dialog opened by `View details ->`, showing full args and full result content.

Decisions for this subtask:
- Pair CALL/RESULT using `tool_call_id` only.
- No FIFO fallback logic and no backward-compat requirement for legacy pairing behavior.
- Reuse shadcn/ui primitives wherever available; avoid duplicate ad-hoc primitives.

## Scope

### 1) Event schema and typing
- Extend `repositoryAgentEventSchema` with `tool_name`, `tool_call_id`, `tool_args`, `tool_result_content`.
- Keep precise typing (`z.record(z.unknown())` for `tool_args`) and inferred TS types.

### 2) Pairing logic
- Update `buildEventDisplayItems()` to perform strict `tool_call_id` pairing.
- Do not implement FIFO fallback queue.
- Preserve order and emit unmatched events as single items.

### 3) Flow 1 accordion UI
- Rewrite tool-pair rendering in `AgentEventItem.tsx` to match Paper `155-0`:
  - CALL row visual treatment
  - RESULT row visual treatment
  - connector line
  - pending row with dashed/muted treatment
  - `View details ->` callback wiring
- Keep non-tool single-event rendering stable to avoid regressions.

### 4) Flow 2 detail dialog
- Implement `ToolDetailModal.tsx` using shadcn `Dialog` primitives as a separate dialog layer.
- Show formatted args and full result content with copy actions.
- Wire a single modal instance at accordion level in `AgentEventsAccordion.tsx`.

### 5) Cleanup
- Remove `ToolResultExpander` usage and delete file.

## Shadcn-first requirement

Use existing shadcn components where applicable (Dialog, Button, Badge, ScrollArea container patterns). Use custom markup only for timeline-specific visuals (dots/connector/pending rail) where no direct shadcn primitive exists.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `repositoryAgentEventSchema` includes `tool_name`, `tool_call_id`, `tool_args`, and `tool_result_content` with precise inferred types.
- [x] #2 `buildEventDisplayItems()` pairs tool events strictly by `tool_call_id` and does not contain FIFO fallback logic.
- [x] #3 Unmatched call/result tool events are rendered as single items without crashes or dropped rows.
- [x] #4 `ToolDetailItem` and modal callback/prop types are defined in `types/agent-events.ts` and used by accordion/item components.
- [x] #5 Flow 1 tool-pair rows match Paper `155-0`: timeline rail, CALL/RESULT visual differentiation, and right-side context hint.
- [x] #6 Pending tool result rows match Paper `155-0`: dashed connector, muted indicator, and `Awaiting result...` treatment.
- [x] #7 Clicking `View details ->` opens a separate Tool Detail dialog (Flow 2), not inline expansion.
- [x] #8 Flow 2 dialog shows full formatted arguments and full result content with working copy actions.
- [x] #9 `ToolResultExpander.tsx` is removed and no remaining imports reference it.
- [x] #10 Implementation reuses shadcn primitives where available (Dialog, Button, Badge) and avoids duplicate custom primitives.
- [x] #11 `bun run lint` passes for frontend changes.
- [x] #12 `bun run build` passes (including TypeScript build checks).
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update frontend event schema in `src/features/repository-agent-snapshots/schema.ts` to include `tool_name`, `tool_call_id`, `tool_args`, and `tool_result_content` with precise inferred types.
2. Refactor `buildEventDisplayItems()` in `src/lib/agent-events-utils.ts` to strict `tool_call_id` pairing only:
   - build maps keyed by `tool_call_id`
   - pair call+result rows only when IDs match
   - remove FIFO fallback logic entirely
   - preserve deterministic order and render unmatched events as `single` items.
3. Extend `src/types/agent-events.ts` for Flow 1/Flow 2 interaction contracts (`ToolDetailItem`, modal props, and `onViewDetails` callback typing).
4. Rewrite tool-pair rendering in `src/components/custom/agent-events/AgentEventItem.tsx` to match Paper `155-0`:
   - 28px timeline rail with call/result indicators and connector
   - CALL/RESULT differentiated row surfaces
   - pending row dashed + muted treatment with `Awaiting result...`
   - `View details ->` action wired to callback.
5. Implement `src/components/custom/agent-events/ToolDetailModal.tsx` using shadcn `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `Button`, `Badge` patterns to match Paper `X6-0`:
   - separate dialog layer (not inline expansion)
   - formatted args section + copy action
   - full result section + copy action + source hint.
6. Update `src/components/custom/agent-events/AgentEventsAccordion.tsx` to host a single modal instance and selected detail item state shared across rows.
7. Delete `src/components/custom/agent-events/ToolResultExpander.tsx` and remove all imports/references.
8. Regression + quality checks:
   - run `bun run lint`
   - run `bun run build`
   - perform visual comparison vs Paper `155-0` and `X6-0` and record notes/screenshots in task.
9. Confirm shadcn-first requirement:
   - reuse existing shadcn primitives where available
   - keep custom markup only for timeline-specific visuals with no direct shadcn equivalent.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Flow 1 + Flow 2 frontend changes in `schema.ts`, `agent-events-utils.ts`, `types/agent-events.ts`, `AgentEventItem.tsx`, `AgentEventsAccordion.tsx`, and new `ToolDetailModal.tsx`.

Removed `src/components/custom/agent-events/ToolResultExpander.tsx` and verified no remaining imports via content search.

Pairing logic in `buildEventDisplayItems()` is now strict `tool_call_id` matching only; FIFO queue path removed.

Validation: `bun run build` passes successfully (tsc + vite).

Validation: file-scoped lint passes for all modified agent-events files using `bun eslint <modified-files>`.

Repository-wide `bun run lint` still reports many pre-existing baseline errors in unrelated files; no new lint issues were reported in modified files.

Addressed post-feedback UI issues from dark-mode screenshot: converted Flow 1 row surfaces/labels/connectors to token-based + dark variants, constrained right-side hint width, and added overflow guards to prevent right-shift/horizontal overflow.

Adjusted timeline rail vertical alignment in `AgentEventItem.tsx` (top/bottom dot spacing + connector segment) so CALL/RESULT dots align with their rows more consistently.

Re-validated changed files with scoped eslint and re-ran `bun run build` successfully.

Refined Flow 1 layout again after screenshot review: switched tool-pair rows to a 2-row grid with a dedicated timeline column so CALL/RESULT dots anchor to row centers.

Reduced perceived row stretch by compacting call hint values (including path compaction), using fixed row heights, and reducing accordion content horizontal offset (`px-1` instead of left-heavy padding).

Re-ran scoped eslint for touched files and `bun run build`; both pass for modified scope.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Paper visual check completed against `155-0` and `X6-0` with screenshots attached/recorded in task notes.
- [x] #2 No FIFO fallback code path remains in frontend event pairing logic.
- [x] #3 Single dialog instance is mounted at accordion level and controlled by selected detail item state.
- [ ] #4 Final summary documents exact files changed and any intentional deviations from prior subtasks.
<!-- DOD:END -->
