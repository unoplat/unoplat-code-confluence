---
id: task-1
title: Fix AGENTS_GENERATION Exception Handling - Propagate Errors to Interceptor
status: Done
assignee: []
created_date: '2025-12-12 07:35'
updated_date: '2026-01-06 11:54'
labels:
  - bug-fix
  - query-engine
  - temporal
dependencies: []
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix bug where repository_agent_md_snapshot status shows COMPLETED with null error_report when agent execution errors occur. Root cause: agent exceptions are caught and swallowed in workflow instead of propagating to interceptor.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Status is ERROR (not COMPLETED) when agent errors occur
- [ ] #2 error_report contains aggregated errors with agent names
- [ ] #3 agent_md_output does NOT contain *_error keys (errors only in error_report)
- [ ] #4 All agents attempted execution (continue & collect all strategy)
- [ ] #5 Partial results preserved in agent_md_output
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Problem
`repository_agent_md_snapshot` status shows "COMPLETED" with `error_report: null` when agent execution errors occur during AGENTS_GENERATION operation. 

Root cause: In `temporal_workflows.py`, agent exceptions are caught and swallowed (logged but not raised), so the interceptor never receives them.

## Solution Design
- **Error Strategy**: "Continue & collect all" - execute all agents, collect errors, then raise ApplicationError at the end
- **Status Semantics**: Use `ERROR` status (not `FAILED`) for partial agent failures since they are common
- **Data Cleanliness**: Do NOT store errors in `agent_md_output` - errors only go in `error_report` column
- **Cascade Failure**: Child workflow failure marks parent as ERROR

## Implementation Changes

### 1. workflow_models.py (commons)
Added ERROR to JobStatus enum:
```python
ERROR = "ERROR"  # Partial failures (some agents succeeded, some failed)
```

### 2. repo_models.py (commons)
Updated CHECK constraints in 2 places:
- `RepositoryWorkflowRun` (line ~121)
- `CodebaseWorkflowRun` (line ~194)

### 3. temporal_workflows.py (query-engine) - PRIMARY FIX
**CodebaseAgentWorkflow changes:**
- Added error tracking list: `agent_errors: list[dict[str, Any]] = []`
- Modified all 3 agent exception handlers to collect errors instead of storing in results
- Added ApplicationError raise at end if any agents failed

**RepositoryAgentWorkflow changes:**
- Added child error tracking: `child_errors: list[dict[str, str]] = []`
- Modified result processing to collect errors not store them
- Added ApplicationError raise AFTER persisting snapshot (preserve partial results)

### 4. agent_workflow_interceptor.py (query-engine)
Changed 4 occurrences of `JobStatus.FAILED.value` to `JobStatus.ERROR.value`:
- Line 231 (RepositoryAgentWorkflow exception handler)
- Line 363 (CodebaseAgentWorkflow exception handler)
- Line 394 (cascade failure check)
- Line 405 (parent workflow status)

### 5. repository_workflow_db_activity.py (query-engine)
- Updated status preservation to include ERROR
- Added ERROR to terminal states list

### 6. codebase_workflow_db_activity.py (query-engine)
- Same changes as repository_workflow_db_activity.py
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Files Modified

| File | Project | Changes |
|------|---------|---------|
| `workflow_models.py` | commons | Added ERROR enum value |
| `repo_models.py` | commons | Updated CHECK constraints (2 places), updated status column comments |
| `temporal_workflows.py` | query-engine | Major error handling refactor - collect errors, raise ApplicationError |
| `agent_workflow_interceptor.py` | query-engine | Changed FAILED → ERROR (4 places) |
| `repository_workflow_db_activity.py` | query-engine | Added ERROR status handling |
| `codebase_workflow_db_activity.py` | query-engine | Added ERROR status handling |

## Key Implementation Details

### ApplicationError Usage
```python
raise ApplicationError(
    error_summary,
    agent_errors,  # Details payload
    type="AgentExecutionError",
    non_retryable=True,
)
```

### Error Collection Pattern
```python
agent_errors.append({
    "agent": "project_configuration_agent",
    "codebase": codebase_metadata.codebase_name,
    "error": str(e),
    "traceback": traceback.format_exc(),
})
```

## Pending Verification
- [ ] Run typecheck: `task typecheck`
- [ ] Run lint: `task lint`
- [ ] Integration test with actual AGENTS_GENERATION workflow

**Database Migration Resolution (2025-12-12):** CHECK constraint violation error occurred because existing PostgreSQL database had old constraints without 'ERROR' status. Resolution: Recreate database tables (alpha project, no migration needed). SQLAlchemy will create tables with updated CHECK constraints that include 'ERROR'.
<!-- SECTION:NOTES:END -->
