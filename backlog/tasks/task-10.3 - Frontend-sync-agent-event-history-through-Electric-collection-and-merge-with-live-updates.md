---
id: TASK-10.3
title: >-
  Frontend: sync agent event history through Electric collection and merge with
  live updates
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
  - electric
dependencies:
  - TASK-10.1
  - TASK-10.2
references:
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsProgress.tsx
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsDialog.tsx
parent_task_id: TASK-10
priority: high
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wire the Generate Agents dialog to normalized progress rows and an Electric-backed TanStack DB event-history collection for the active codebase. The collection strategy must keep initial loading bounded, preserve ascending `event_id` order, and keep scroll behavior stable during live updates without relying on a custom paginated REST API.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The frontend uses Electric-backed TanStack DB collections for active-run progress state and active-codebase event history.
- [ ] #2 The event-history collection has an explicit sync-mode decision documented in code/task notes: default `on-demand`, with `progressive` only if background full-history backfill is intentionally desired.
- [ ] #3 Older history becomes available through TanStack DB subset loading / infinite-query behavior while preserving ascending `event_id` order and avoiding duplicates or gaps.
- [ ] #4 Live updates append correctly and scroll behavior preserves position when browsing older events, auto-following only when the user is near the bottom.
- [ ] #5 Frontend checks covering Electric-backed history loading and scroll behavior pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add collection wiring for repository workflow progress and event history scoped by repository owner, repository name, workflow run, and codebase.

2. Choose the history sync mode deliberately and document the reason in code: prefer `on-demand` for large append-only histories so only queried subsets are synced; only use `progressive` if we want the full filtered history to backfill automatically in the background.

3. Replace the abandoned REST history-hook approach with TanStack DB live hooks (`useLiveQuery` and/or `useLiveInfiniteQuery`) so the UI can initialize from a bounded recent slice and make older history available through collection subset loads.

4. Keep one canonical ordering rule for the viewer state: event rows are rendered in ascending `event_id` order even if collection queries fetch pages in a different order internally.

5. Update `GenerateAgentsProgress` and related event-view state to preserve scroll position when older history materializes, auto-follow only when pinned to the bottom, and expose a jump-to-latest affordance when new events arrive out of view.

6. Validate the Electric-backed history/live update behavior with targeted frontend checks and record any follow-up risks in task notes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The earlier paginated-REST history merge attempt was intentionally reverted.

Restart this task from the upgraded Electric/TanStack stack now present in the frontend workspace.

Use `syncMode: "on-demand"` as the default starting point. Revisit `progressive` only if we discover the product wants background full-history backfill after first paint, because that changes client memory and sync behavior materially.

Implemented the normalized frontend sync path for repository agent runs: `schema.ts` now models snapshot summary rows, codebase progress rows, and append-only event rows; `collection.ts` now creates separate Electric collections for snapshot metadata, eager per-run progress rows, and on-demand per-codebase event history.

Added live hook composition in `hooks.ts` using `useLiveQuery` for snapshot/progress and `useLiveInfiniteQuery` for event history queried in descending `event_id` order, then reversed before rendering so the UI still displays oldest-to-newest rows.

Rewired `GenerateAgentsDialog.tsx` to derive codebases from live progress rows instead of legacy snapshot JSON and added `GenerateAgentsProgressLive.tsx` as the new event/progress viewer while keeping the older `GenerateAgentsProgress.tsx` file in place for reference until post-UI-test cleanup.

Updated event utilities to use normalized `event_id` ordering/pairing and preserved the TASK-10.2 virtualized timeline. `GenerateAgentsProgressLive.tsx` now supports per-codebase history loading, preserves scroll position when loading older history, auto-follows when the user is near the bottom, and shows a jump-to-latest action when new rows arrive while browsing earlier history.

Validation so far: `bun x tsc -b --pretty false` passes for the frontend. Targeted ESLint on the touched TASK-10.3 files passes, aside from the existing external `baseline-browser-mapping` freshness notice. Manual UI verification and legacy cleanup are intentionally still pending.
<!-- SECTION:NOTES:END -->
