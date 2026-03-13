---
id: TASK-10.1
title: >-
  Backend: persist agent events in normalized history for Electric-backed
  frontend sync
status: Done
assignee:
  - codex
created_date: '2026-03-08 08:43'
updated_date: '2026-03-10 09:31'
labels:
  - backend
  - performance
  - events
  - electric
dependencies: []
references:
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/tracking/repository_agent_snapshot_service.py
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/__init__.py
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-query-engine/pyproject.toml
  - >-
    /Users/jayghiya/.superset/worktrees/unoplat-code-confluence/update-commons-testing/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py
parent_task_id: TASK-10
priority: high
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Normalize repository agent runtime state so durable event history and live progress live outside the snapshot JSON payload, and shape those tables so the frontend can sync them directly with Electric.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Shared commons models exist for durable repository agent events and per-run/per-codebase live progress.
- [ ] #2 Snapshot/runtime persistence allocates event ids and updates progress from normalized rows while keeping runtime state out of `RepositoryAgentMdSnapshot` except for any explicitly temporary rollout fields.
- [ ] #3 The history and progress tables are keyed/indexed so Electric can sync one repository workflow run and codebase efficiently with deterministic `event_id` ordering.
- [ ] #4 Backend tests covering event persistence, progress updates, and snapshot finalization/tail behavior are added or updated and pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add normalized commons ORM models for `repository_agent_event` and `repository_agent_codebase_progress`, keyed by repository owner, repository name, workflow run id, and codebase name.

2. Standardize durable history on integer `event_id` values and shape the event table for Electric filtering/order with deterministic per-codebase ordering via the composite primary key/index strategy.

3. Refactor `RepositoryAgentSnapshotWriter.begin_run()` to seed the snapshot row plus per-codebase progress rows without resetting an existing run's normalized history.

4. Refactor `RepositoryAgentSnapshotWriter.append_event_atomic()` so one transaction locks the progress row, allocates the next event id, updates completed namespaces/progress counters, inserts a normalized event row, and refreshes snapshot summary fields like `overall_progress` and `latest_event_at`.

5. Keep `RepositoryAgentMdSnapshot` focused on final output/statistics/PR metadata plus temporary summary rollout fields, with normalized tables becoming the source of truth for event history and live progress.

6. Defer automated tests for now at user request; focus this pass on backend/schema implementation only, then surface any follow-up validation gaps in task notes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
This task should be treated as a clean-slate backend implementation plan.

Do not invest further in the previous paginated history API path unless another feature explicitly requires it; it is no longer the target source of truth for frontend history loading.

The commons dependency bump to `unoplat-code-confluence-commons-v0.45.0` is intentional and should be preserved because this task expects new shared models to land there.

User approved starting implementation immediately and explicitly asked to defer tests for now so this pass is backend/schema only.

Implemented normalized backend storage pass: added `RepositoryAgentEvent` and `RepositoryAgentCodebaseProgress` in commons, removed snapshot runtime JSON fields from `RepositoryAgentMdSnapshot`, refactored `RepositoryAgentSnapshotWriter.begin_run()` and `append_event_atomic()` to seed/update normalized rows, standardized event ids to integers, and removed the unused legacy `repository_event_progress_tracker.py` helper.

Validation for this pass: targeted `basedpyright` on the changed query-engine files passed, targeted `ruff check` on the changed query-engine files passed, and `uv run python` successfully imported the updated commons ORM models. Full repo typecheck still has unrelated pre-existing failures outside TASK-10.1 scope.
<!-- SECTION:NOTES:END -->
