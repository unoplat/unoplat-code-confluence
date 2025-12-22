---
id: doc-005
title: Agent MD Snapshot Persistence - Restore Final Payload & Statistics
type: other
created_date: '2025-12-09 07:45'
updated_date: '2025-12-10 10:21'
---
# Agent MD Snapshot Persistence - Restore Final Payload & Statistics

> **Purpose**: Implementation plan to restore agent MD output persistence after Temporal migration (PR #1044). Status tracking is now handled by Temporal via `RepositoryWorkflowRun` - we only need to persist `agent_md_output` and `statistics`.

---

## Executive Summary

### Key Insight: Two Separate Systems

| System | Table | Purpose | Status Tracking |
|--------|-------|---------|-----------------|
| **Temporal Workflow** | `RepositoryWorkflowRun` | Workflow execution state | SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING |
| **Agent Output** | `RepositoryAgentMdSnapshot` | Store generated content | ~~RUNNING, COMPLETED, ERROR~~ **→ Remove** |

**Decision**: Since Temporal now handles all status tracking via `RepositoryWorkflowRun`, we should:
1. **Remove** `status` field from `RepositoryAgentMdSnapshot`
2. **Remove** `RepoAgentSnapshotStatus` enum from commons
3. **Keep** `complete_run()` but only for `agent_md_output` and `statistics` persistence
4. **Remove** `fail_run()` (no longer needed without status field)

---

## Current State (Post-Temporal Migration)

| Component | Status | Notes |
|-----------|--------|-------|
| `begin_run()` | ✅ Called | In `workflow_service.py:109-115` - initializes snapshot row |
| `append_event_atomic()` | ✅ Called | In `temporal_agents.py` - event streaming works |
| `complete_run()` | ❌ NOT Called | **Gap**: `agent_md_output` and `statistics` not persisted |
| `fail_run()` | 🗑️ Remove | No longer needed - Temporal tracks errors |
| `status` field | 🗑️ Remove | Redundant - Temporal tracks status in `RepositoryWorkflowRun` |

---

## ⚠️ Critical Bug Fix: Cross-Run Corruption

### Problem Identified

The `complete_run()` method and `AgentSnapshotCompleteEnvelope` have a critical bug that causes **cross-run data corruption**:

| Component | Has `run_id`? | Issue |
|-----------|---------------|-------|
| `RepositoryAgentMdSnapshot` PK | ✅ YES | 3-part composite key: `(owner, repo, run_id)` |
| `begin_run()` | ✅ YES | Correctly includes `repository_workflow_run_id` |
| `AgentSnapshotCompleteEnvelope` | ❌ NO | Missing `repository_workflow_run_id` field |
| `complete_run()` WHERE clause | ❌ NO | Only filters by `(owner, repo)` - matches ALL runs! |

### Corruption Scenario

When multiple workflow runs exist for the same repository:

1. **Run A starts**: Creates row `(owner, repo, run_id_A)` with empty `agent_md_output`
2. **Run B starts**: Creates row `(owner, repo, run_id_B)` with empty `agent_md_output`
3. **Run A completes**: `complete_run(owner, repo, payload_A)` executes:
   ```sql
   UPDATE repository_agent_md_snapshot 
   SET agent_md_output = payload_A
   WHERE owner = 'owner' AND repo = 'repo'
   -- ^^^ Matches BOTH rows! Updates A and B to payload_A
   ```
4. **Run B completes**: Same issue - overwrites BOTH rows with `payload_B`

**Result**: Both rows have `payload_B`, Run A's data is lost forever.

### Required Fix (Part of task-011)

1. **Add `repository_workflow_run_id` to `AgentSnapshotCompleteEnvelope`**
2. **Update `complete_run()` signature** to accept `repository_workflow_run_id`
3. **Update `complete_run()` WHERE clause** to include `repository_workflow_run_id`
4. **Update workflow** to pass `repository_workflow_run_id` when creating envelope
5. **Update activity** to pass `repository_workflow_run_id` to `complete_run()`

---

## Implementation Plan

### Task 1: Remove Status from Commons (task-007) ✅ DONE

**File**: `unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py`

**Changes**:
1. Delete `RepoAgentSnapshotStatus` enum (lines 21-27)
2. Remove `status` field from `RepositoryAgentMdSnapshot` (lines 365-374)
3. Clean up any unused imports

---

### Task 2: Update RepositoryAgentSnapshotWriter (task-009)

**File**: `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/tracking/repository_agent_snapshot_service.py`

**Changes**:

1. **Remove** `RepoAgentSnapshotStatus` import (line 12)

2. **Update `begin_run()`** - Remove status initialization

3. **Update `complete_run()`** - Remove status update, keep only `agent_md_output` and `statistics`
   - **CRITICAL**: Add `repository_workflow_run_id` parameter
   - **CRITICAL**: Add `repository_workflow_run_id` to WHERE clause

4. **Delete `fail_run()`** method entirely (lines 440-462)

5. **Update or remove `get_active_run_id()`** - needs redesign since it checks for RUNNING status

---

### Task 3: Update API Endpoint (task-010)

**File**: `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`

**Changes**:
- Remove `status` from response
- Add `statistics` to response if not already included
- If frontend needs status, fetch from `RepositoryWorkflowRun` via join

---

### Task 4: Add complete_run() Call to Temporal Workflow (task-011) - UPDATED

**Files to modify**:
1. `workflow_envelopes.py` - Add `repository_workflow_run_id` to `AgentSnapshotCompleteEnvelope`
2. `temporal_workflows.py` - Pass `repository_workflow_run_id` when creating envelope
3. `repository_agent_snapshot_activity.py` - Pass `repository_workflow_run_id` to `complete_run()`
4. `repository_agent_snapshot_service.py` - Accept and use `repository_workflow_run_id` in `complete_run()`

**Envelope Update**:
```python
class AgentSnapshotCompleteEnvelope(BaseModel):
    owner_name: str
    repo_name: str
    repository_workflow_run_id: str  # NEW - Required for correct row targeting
    final_payload: dict[str, Any]
    statistics_payload: Optional[dict[str, Any]] = None
```

**Workflow Update** (lines 318-335):
```python
owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
complete_envelope = AgentSnapshotCompleteEnvelope(
    owner_name=owner_name,
    repo_name=repo_name,
    repository_workflow_run_id=repository_workflow_run_id,  # NEW
    final_payload=results,
    statistics_payload=None,
)
```

**complete_run() Update**:
```python
async def complete_run(
    self,
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,  # NEW
    final_payload: dict[str, object],
    statistics_payload: dict[str, object] | None = None,
) -> None:
    async with get_startup_session() as session:
        stmt = (
            update(RepositoryAgentMdSnapshot)
            .where(
                RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                RepositoryAgentMdSnapshot.repository_name == repo_name,
                RepositoryAgentMdSnapshot.repository_workflow_run_id == repository_workflow_run_id,  # NEW
            )
            .values(
                agent_md_output=final_payload,
                statistics=statistics_payload,
                modified_at=func.now(),
            )
        )
        await session.execute(stmt)
```

---

### Future: Add Statistics Collection (task-013)

Collect usage statistics from agent runs and pass to `complete_run()`:

1. Capture `UsageSummary` from each `TemporalAgent.run()` result
2. Aggregate per-codebase using `_build_workflow_statistics()` pattern
3. Pass to `complete_run()` as `statistics_payload`

---

## Files to Modify

| File | Changes |
|------|---------|
| `commons/repo_models.py` | Remove `RepoAgentSnapshotStatus`, remove `status` field |
| `query-engine/services/tracking/repository_agent_snapshot_service.py` | Update `begin_run()`, `complete_run()` (add run_id), remove `fail_run()` |
| `query-engine/services/temporal/workflow_envelopes.py` | Add `repository_workflow_run_id` to envelope |
| `query-engine/services/temporal/temporal_workflows.py` | Pass `repository_workflow_run_id` to envelope |
| `query-engine/services/temporal/activities/repository_agent_snapshot_activity.py` | Pass `repository_workflow_run_id` to `complete_run()` |
| `query-engine/api/v1/endpoints/codebase_agent_rules.py` | Update response (remove status) |

---

## Dependencies

```
task-007: Remove from commons ✅ DONE
    ↓
task-009: Update writer service (includes complete_run signature fix)
    ↓
task-010: Update API  +  task-011: Add complete_run() call (with run_id fix)
    ↓
task-013: Statistics (future)
```

---

## Deferred Tasks

| Task | Reason |
|------|--------|
| DB Migration (drop status column) | Not required now - column can remain unused |
| Frontend schema update | Will tackle later when frontend changes are needed |

---

## Notes

- **Why remove status?** Temporal already tracks workflow status via interceptors that update `RepositoryWorkflowRun`. Having a second status field creates confusion and potential inconsistency.

- **Error handling**: Workflow errors are tracked by Temporal in `RepositoryWorkflowRun.status` = FAILED. No need for `fail_run()`.

- **Frontend impact**: Frontend should query `RepositoryWorkflowRun.status` for execution state, and `RepositoryAgentMdSnapshot` only for the output content.

- **No DB migration needed**: The `status` column will remain in the database but won't be used. Can be cleaned up later if needed.

- **Cross-run corruption fix**: The `repository_workflow_run_id` must be passed through the entire chain (workflow → envelope → activity → service) to ensure each run's output is isolated to its own database row.
