---
id: TASK-4.1
title: >-
  Backend: Store full tool context in events JSONB (tool_name, tool_args,
  tool_call_id, tool_result_content)
status: Done
assignee: []
created_date: '2026-03-02 08:01'
updated_date: '2026-03-10 09:31'
labels:
  - backend
  - python
  - electric-sql
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/events/agent_events.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/event_stream_handler.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/tracking/repository_agent_snapshot_service.py
parent_task_id: TASK-4
priority: high
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context

`event_stream_handler.py` currently extracts `tool_call_id`, `tool_name`, and `tool_args` from the PydanticAI event stream but discards all three — they are only used in log lines. Tool result content is truncated to 100 characters before being stored in the `message` field.

This subtask persists all four fields into the `events` JSONB column of `repository_agent_md_snapshot` so that the frontend can display full structured tool information without any data loss.

## What to Change

### File 1: `agent_events.py`
Extend `AgentEventPayload` with four new optional fields:
```python
from typing import Any, Optional
# Add to AgentEventPayload:
tool_name: Optional[str] = None
tool_call_id: Optional[str] = None
tool_args: Optional[dict[str, Any]] = None        # nested JSONB object
tool_result_content: Optional[str] = None         # raw content, capped at 100_000 chars
```

### File 2: `event_stream_handler.py`
**Add top-level helper** `_extract_tool_args(event: AgentStreamEvent) -> dict[str, Any] | None`:
- `if isinstance(event, FunctionToolCallEvent)`: return `event.part.args` if already `dict`, else `json.loads(event.part.args)`
- Otherwise: return `None`

**Update `_extract_event_message()`**:
- Increase `FunctionToolResultEvent` preview from `[:100]` to `[:200]` (backward-compat display message).

**Update main `event_stream_handler()` loop**:
- Extract `tool_name`: `event.part.tool_name` for `FunctionToolCallEvent`, else `None`
- Extract `tool_call_id`: reuse existing `_extract_tool_call_id(event)` helper (already handles both event types)
- Extract `tool_args`: call `_extract_tool_args(event)` (non-None only for call events)
- Extract `tool_result_content`: `str(event.result.content)[:100_000]` for `FunctionToolResultEvent`, else `None` — **raw content, NO "Tool result: " prefix**
- Pass all four to `append_event_atomic()`

### File 3: `repository_agent_snapshot_service.py`
**Extend `append_event_atomic` signature** (all new params keyword-only, default `None`):
```python
tool_name: str | None = None,
tool_call_id: str | None = None,
tool_args: dict[str, Any] | None = None,
tool_result_content: str | None = None,
```

**Update `new_event_obj` CTE** — wrap `jsonb_build_object` with `jsonb_strip_nulls`:
```sql
SELECT jsonb_strip_nulls(jsonb_build_object(
    'id', opc.allocated_id,
    'event', :agent_name,
    'phase', :phase,
    'message', CAST(:message AS text),
    'tool_name', CAST(:tool_name AS text),
    'tool_call_id', CAST(:tool_call_id AS text),
    'tool_args', CAST(:tool_args AS jsonb),
    'tool_result_content', CAST(:tool_result_content AS text)
)) AS event_obj
```

Pass `tool_args` as `json.dumps(tool_args)` from Python (or `None`). Add new bind params to the `session.execute(...)` call.

## Key Technical Notes

- `_extract_tool_call_id(event)` already exists — reuse, do NOT duplicate
- `event.part.args` can be `dict` or `str`; use `isinstance(event.part.args, dict)` guard before `json.loads`
- `jsonb_strip_nulls` removes JSON keys whose value is SQL NULL — prevents storing `"tool_args": null` for non-call events
- Import `json` and `Any` at module top-level (no nested imports per CLAUDE.md)
- Use `dict[str, Any]` not `dict[str, any]` or `Dict`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 AgentEventPayload has tool_name, tool_call_id, tool_args, tool_result_content fields (all Optional, default None)
- [x] #2 append_event_atomic accepts four new keyword params (all default None)
- [x] #3 tool_args passed as json.dumps() string from Python and CAST to jsonb in SQL
- [x] #4 tool_result_content stored as raw text capped at 100_000 chars with no Tool result: prefix
- [x] #5 FunctionToolResultEvent message preview increased from 100 to 200 chars
- [x] #6 Existing _extract_tool_call_id() helper reused — not duplicated
- [x] #7 _extract_tool_args() is a top-level function (not nested)
- [x] #8 uv run pyright: 0 errors in modified files
- [x] #9 uv run ruff check: 0 new issues in modified files
- [x] #10 SQL `new_event_obj` uses `jsonb_strip_nulls(jsonb_build_object(...))` and includes keys `id`, `event`, `phase`, `message`, `tool_name`, `tool_call_id`, `tool_args`, and `tool_result_content`.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## Changes Made

**`agent_events.py`**: Added `Any` to typing imports; extended `AgentEventPayload` with `tool_name: Optional[str]`, `tool_call_id: Optional[str]`, `tool_args: Optional[dict[str, Any]]`, `tool_result_content: Optional[str]` — all default `None`.

**`event_stream_handler.py`**: Added `json`, `Any` imports; added two top-level helpers `_extract_tool_args()` (handles `dict | str | None` args) and `_extract_tool_result_content()` (caps at 100_000 chars, no prefix); increased message preview from `[:100]` to `[:200]`; passes all four new fields to `append_event_atomic()`.

**`repository_agent_snapshot_service.py`**: Added `json` import; extended `append_event_atomic` with four optional keyword params; updated `new_event_obj` CTE to use `jsonb_strip_nulls(jsonb_build_object(...))` with all eight keys; passes `tool_args` as `json.dumps()` string cast to jsonb.

**Verification**: `task typecheck-file` → 0 errors on all three files. `task lint` → all checks passed.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 uv run pyright returns 0 errors on all three modified files
- [ ] #2 uv run ruff check returns 0 new issues
- [ ] #3 All acceptance criteria checked
- [ ] #4 Final summary written with exact diffs described
<!-- DOD:END -->
