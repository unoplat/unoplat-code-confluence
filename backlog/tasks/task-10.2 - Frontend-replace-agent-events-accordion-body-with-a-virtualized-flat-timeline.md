---
id: TASK-10.2
title: 'Frontend: replace agent events accordion body with a virtualized flat timeline'
status: Done
assignee:
  - codex
created_date: '2026-03-08 08:43'
updated_date: '2026-03-10 09:31'
labels:
  - frontend
  - performance
  - react
  - events
  - tanstack
dependencies: []
references:
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsProgress.tsx
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventsAccordion.tsx
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventItem.tsx
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/types/agent-events.ts
parent_task_id: TASK-10
priority: high
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor the agent events viewer so it no longer renders nested accordion content for all events. The new view must use a flat row model with virtualization, preserve agent grouping and tool call/result pairing, and consume already-normalized event/progress data rather than parsing snapshot runtime JSON.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The active codebase event viewer renders through a flat virtualized timeline instead of mapping every event row into the DOM.
- [ ] #2 Agent grouping, strict `tool_call_id` pairing, and detail modal behavior remain correct in the new virtualized timeline.
- [ ] #3 The renderer consumes ordered event rows plus progress metadata from upstream hooks/collections and does not depend on snapshot `events` JSON as its long-term data contract.
- [ ] #4 Frontend checks covering the virtualized event viewer pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Refactor the current agent event utility layer so grouping and strict `tool_call_id` pairing can feed a flat row model instead of nested accordion content.

2. Keep the public `AgentEventsAccordion` entrypoint but replace its internals with a flat TanStack Virtual timeline using one scroll container, stable row keys, sticky group headers, and measured variable-height rows.

3. Reuse `AgentEventItem`, `AgentGroupHeader`, and `ToolDetailModal` so existing event visuals and detail interactions stay intact while only the rendering strategy changes.

4. Keep the renderer decoupled from collection-loading details: it should accept normalized ordered events and progress metadata from TASK-10.3 rather than owning sync-mode decisions itself.

5. Run targeted frontend validation for the virtualized timeline changes and record any compatibility deviations in task notes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
A previous partially wired virtualized implementation was intentionally reverted.

Rebuild this task against the final Electric-based data contract, not against the legacy snapshot `events` JSON shape and not against the abandoned paginated REST history hook.

This task owns rendering performance and UI correctness; TASK-10.3 owns how events arrive in memory.

Official TanStack Virtual docs were reviewed in the existing Chrome session before implementation planning:
- `https://tanstack.com/virtual/latest/docs/api/virtualizer`
- `https://tanstack.com/virtual/latest/docs/framework/react/examples/sticky`
- `https://tanstack.com/virtual/latest/docs/framework/react/examples/dynamic`

Implementation guidance from those docs for this task:
- Keep one scroll container and one relative inner sizing element driven by `rowVirtualizer.getTotalSize()`; virtual rows should remain absolutely positioned with `translateY(...)`.
- Use `measureElement` for event rows because both group headers and event cards have variable height; pair it with a conservative `estimateSize` rather than relying on fixed-height assumptions.
- Provide a memoized `getItemKey` based on stable timeline row ids instead of raw indexes so measurement cache churn stays low when live data changes.
- Use a custom `rangeExtractor` layered on `defaultRangeExtractor` to keep the active sticky group header rendered even when its natural row is outside the visible range.
- Follow the sticky example pattern: active group header can switch to `position: sticky` while non-active rows stay absolutely positioned.
- Keep the virtualizer configuration friendly to future live-update scroll work in TASK-10.3, especially around stable keys, measured rows, and potential use of `shouldAdjustScrollPositionOnItemSizeChange` if dynamic row remeasurement would otherwise shift the viewport unexpectedly.

Implemented a new TanStack Virtual-based flat timeline renderer in `unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventsTimeline.tsx` and switched `AgentEventsAccordion` to delegate to it while preserving the old accordion markup in `unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventsAccordionLegacy.tsx` for UX/reference parity until cleanup.

Added flat row utilities and types so grouped agent headers and paired tool-call/result rows can be rendered as one virtualized list with stable row keys and sticky section headers.

Updated `GenerateAgentsProgress` to pass the existing scroll viewport ref into the virtualized timeline and switched auto-scroll behavior from `smooth` to `auto` to avoid TanStack Virtual dynamic-measurement smooth-scroll issues called out in the docs.

Validation: targeted ESLint passed on the changed TASK-10.2 files. A targeted TypeScript check for the TASK-10.2 files also passed before removing the temporary local-only tsconfig helper. Full frontend typecheck remains blocked by the pre-existing TanStack DB type mismatch in `src/features/repository-agent-snapshots/collection.ts`.
<!-- SECTION:NOTES:END -->
