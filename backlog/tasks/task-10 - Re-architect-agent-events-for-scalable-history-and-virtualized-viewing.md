---
id: TASK-10
title: Re-architect agent events for scalable history and virtualized viewing
status: Done
assignee:
  - codex
created_date: '2026-03-08 08:43'
updated_date: '2026-03-10 09:31'
labels:
  - backend
  - frontend
  - performance
  - tanstack
  - events
dependencies: []
references:
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/tracking/repository_agent_snapshot_service.py
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsProgress.tsx
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventsAccordion.tsx
documentation:
  - 'https://tanstack.com/db/latest/docs/framework/react/overview'
  - 'https://tanstack.com/db/latest/docs/collections/electric-collection'
  - 'https://tanstack.com/virtual/latest/docs/introduction'
  - 'https://electric-sql.com/docs/guides/shapes'
priority: high
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the approved redesign for repository agent events so the Generate Agents dialog remains responsive when repositories retain very large event histories. The work must separate live summary state from durable event history, keep initial dialog load bounded, replace the current nested accordion rendering path with a flat virtualized timeline, and source event history from an Electric-backed TanStack DB collection instead of a custom paginated REST flow.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Generate Agents dialog remains responsive when event history is very large because initial live state stays bounded and does not depend on syncing one giant snapshot document.
- [ ] #2 Durable event history is stored separately from the live snapshot and can be consumed through an Electric-backed TanStack DB collection scoped to the active repository workflow run and codebase.
- [ ] #3 Frontend event viewing uses a flat virtualized timeline with agent grouping, correct tool call/result pairing, and stable behavior for live updates.
- [ ] #4 Historical events for the active codebase can be incrementally loaded through Electric collection sync without duplicates, gaps, or scroll-position regressions.
- [ ] #5 Backend and frontend automated checks covering the changed areas are added or updated and pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Finalize the normalized backend design around three stores: `repository_agent_event` for durable history, `repository_agent_codebase_progress` for live counters/progress/completions, and `repository_agent_md_snapshot` for final output/statistics/PR metadata only.

2. Move shared persistence models into commons and ensure the history/progress tables are indexed and keyed so Electric shapes can filter by repository owner, repository name, workflow run, and codebase while preserving deterministic event ordering.

3. Rework writer logic so event-id allocation, progress updates, and completion tracking happen atomically from the normalized codebase-progress row rather than snapshot JSON fields.

4. Point the frontend live experience at normalized progress rows plus an Electric-backed TanStack DB event-history collection. Default the event-history collection to `syncMode: "on-demand"`; only switch to `progressive` if the product explicitly wants the full filtered history to backfill in the background.

5. Keep the event viewer as a flat virtualized timeline so render cost stays bounded even after older history is loaded into the client.

6. Remove `events`, `event_counters`, and `codebase_progress` from `RepositoryAgentMdSnapshot` only after backend and frontend have fully switched to the new normalized sources.

7. Validate with targeted backend tests for id allocation, progress updates, Electric-compatible history reads, and snapshot finalization plus frontend build/lint once the UI is switched.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The previous paginated-REST/history-hook attempt was intentionally reverted so this task can restart from a clean slate.

The prerequisites that remain intentionally in place are: frontend Electric/TanStack dependency upgrades, frontend skill mappings, Electric Docker image updates, and the commons dependency bump.

Task split going forward:
- TASK-10.1 owns backend normalized storage and Electric-friendly schema/table shape.
- TASK-10.2 owns the flat virtualized renderer only.
- TASK-10.3 owns TanStack DB/Electric collection wiring, sync-mode choice, and viewer-state behavior.

Current default: use `syncMode: "on-demand"` for event history because the dataset is append-only and potentially unbounded. Only choose `progressive` if we explicitly want the full filtered history to sync into the client after first paint.
<!-- SECTION:NOTES:END -->
