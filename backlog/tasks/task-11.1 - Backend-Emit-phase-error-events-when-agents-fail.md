---
id: TASK-11.1
title: 'Backend: Emit phase="error" events when agents fail'
status: To Do
assignee: []
created_date: '2026-03-08 14:34'
updated_date: '2026-03-19 09:57'
labels:
  - backend
  - temporal
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
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/event_stream_handler.py
parent_task_id: TASK-11
priority: high
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context

This is the backend half of TASK-11 (Surface agent failures in UI via error events). Currently, when agents fail in `temporal_workflows.py`, errors are collected in-memory in `agent_errors` list but never persisted as events to the `repository_agent_event` table.

## What to build

### 1. New Temporal activity: `AgentErrorEventActivity`

**New file**: `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/agent_error_event_activity.py`

Follow the exact pattern of `EngineeringWorkflowCompletionActivity` (55 lines). Create a class with a single `@activity.defn` method `emit_agent_error_event` that:
- Accepts: `repository_qualified_name`, `repository_workflow_run_id`, `codebase_name`, `agent_name`, `error_message`, `programming_language`
- Parses `owner_name/repo_name` from `repository_qualified_name`
- Calls `get_snapshot_writer().append_event_atomic(phase="error", agent_name=agent_name, message=error_message, completion_namespaces=set(get_completion_namespaces(programming_language)))`

**Why an activity?** The error `except` blocks are inside the Temporal workflow sandbox. DB calls must happen in activities for determinism.

**Why `phase="error"` works without migration**: The `RepositoryAgentEvent.phase` column is `Mapped[str]` (no check constraint). The `append_event_atomic` method's completion tracking only triggers for `phase == "result"` (line 181), so `"error"` naturally bypasses it.

### 2. Register activity in worker manager

**File**: `temporal_worker_manager.py`
- Import `AgentErrorEventActivity` (line ~55 area)
- Instantiate after line 340: `agent_error_event_activity = AgentErrorEventActivity()`
- Add `agent_error_event_activity.emit_agent_error_event` to `activities=[...]` list (line 375)

### 3. Emit error events from except blocks in temporal_workflows.py

**Import**: Add `AgentErrorEventActivity` import inside `with workflow.unsafe.imports_passed_through():` block.

**6 error catch sites** need the activity call (after building `error_entry`, before `agent_errors.append(...)`):

| Location | Agent name | Lines (approx) |
|----------|-----------|----------------|
| `_run_section_updater` except block | `updater_agent_name` (dynamic) | ~192-213 |
| `_run_call_expression_validation` except block | `"call_expression_validator"` | ~323-349 |
| `development_workflow_guide` except block | `"development_workflow_guide"` | ~484-504 |
| `dependency_guide` outer except block | `"dependency_guide"` | ~615-635 |
| `business_domain_guide` except block | `"business_domain_guide"` | ~699-721 |
| `app_interfaces_agent` except block | `"app_interfaces_agent"` | ~801-821 |

**Pattern for each site** (wrap in try/except for resilience):
```python
try:
    await workflow.execute_activity(
        AgentErrorEventActivity.emit_agent_error_event,
        args=[repository_qualified_name, repository_workflow_run_id,
              codebase_metadata.codebase_name, agent_name,
              f"{agent_name} failed: {str(e)[:500]}",
              codebase_metadata.codebase_programming_language or ""],
        start_to_close_timeout=timedelta(seconds=30),
        retry_policy=DB_ACTIVITY_RETRY_POLICY,
    )
except Exception as emit_err:
    logger.warning("[workflow] Failed to emit error event for {}: {}", agent_name, emit_err)
```

**Note on per-dependency-item failures** (~line 561-568): These only log a warning and don't add to `agent_errors`. The overall `dependency_guide` still completes. Do NOT emit error events for these — they are tolerated by design.

## Verification
1. `uv run basedpyright` — typecheck
2. `uv run ruff check` — lint
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 New `AgentErrorEventActivity` class follows the pattern of `EngineeringWorkflowCompletionActivity` with a single `@activity.defn` method
- [ ] #2 Activity is registered in `temporal_worker_manager.py` (imported, instantiated, added to activities list)
- [ ] #3 All 6 agent-level except blocks in `temporal_workflows.py` emit `phase="error"` events via the new activity
- [ ] #4 Error event uses the failing agent's own name (e.g., `business_domain_agents_md_updater`) so frontend aliases group it correctly
- [ ] #5 Error message is truncated to 500 chars for display safety
- [ ] #6 Each error emission call is wrapped in try/except to preserve workflow resilience
- [ ] #7 Per-dependency-item failures (line ~561) are NOT included — they are tolerated partial failures
- [ ] #8 basedpyright and ruff check pass cleanly
<!-- AC:END -->
