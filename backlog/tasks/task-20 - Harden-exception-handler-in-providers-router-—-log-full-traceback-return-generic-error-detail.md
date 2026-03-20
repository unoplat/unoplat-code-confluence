---
id: TASK-20
title: >-
  Harden exception handler in providers router — log full traceback, return
  generic error detail
status: To Do
assignee: []
created_date: '2026-03-19 13:30'
labels:
  - security
  - logging
  - error-handling
  - flow-bridge
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/providers/router.py
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**File:** `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/providers/router.py` (lines 56–60)

**Current behaviour (verified):**
```python
except Exception as exc:
    logger.error("GraphQL Error: {}", str(exc))
    raise HTTPException(
        status_code=500, detail=f"Failed to fetch repositories: {str(exc)}"
    )
```

Two problems:
1. `logger.error` only logs the stringified message — no stack trace, making production debugging harder.
2. `HTTPException.detail` leaks raw exception text to the API consumer, which can expose internals.

**Required changes:**

1. **Logging** — replace `logger.error("GraphQL Error: {}", str(exc))` with a call that captures the full stack trace. Use either:
   - `logger.exception("GraphQL Error: {}", str(exc))` (Loguru auto-attaches traceback), or
   - `logger.error("GraphQL Error: {}", str(exc), exc_info=exc)`.
   The full exception details must remain **only in logs**.

2. **HTTPException detail** — change the detail to a stable, generic message:
   ```python
   raise HTTPException(status_code=500, detail="Failed to fetch repositories")
   ```
   Do **not** include `str(exc)` in the detail.

**Verification:** After making the change, confirm each finding against the current code and only fix it if needed. Ensure no other callers depend on the dynamic detail string (search for usages of the detail text in tests and frontend).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Exception block uses logger.exception (or logger.error with exc_info) so full stack trace is captured in logs
- [ ] #2 HTTPException detail is a stable generic string 'Failed to fetch repositories' — no str(exc) leaked to the client
- [ ] #3 Existing tests still pass after the change
- [ ] #4 No frontend or test code depends on the dynamic detail string (verified via search)
<!-- AC:END -->
