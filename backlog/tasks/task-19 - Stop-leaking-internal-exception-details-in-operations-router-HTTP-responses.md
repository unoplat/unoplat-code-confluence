---
id: TASK-19
title: Stop leaking internal exception details in operations router HTTP responses
status: To Do
assignee: []
created_date: '2026-03-19 13:29'
labels:
  - security
  - flow-bridge
  - api
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/operations/router.py
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The two GET endpoints in `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/operations/router.py` currently embed raw `str(e)` in the `HTTPException.detail` field, which sends internal exception text (stack traces, DB errors, etc.) to API clients.

**Current behaviour (lines 71-76 and 114-119):**
```python
except Exception as e:
    logger.error("Error retrieving parent workflow jobs: {}", str(e))
    raise HTTPException(
        status_code=500,
        detail="Error retrieving parent workflow jobs: {}".format(str(e)),
    )
```

The same pattern repeats for the `/get/ingestedRepositories` endpoint.

**Desired behaviour:**
- Replace the `detail` string with a generic, user-safe message (e.g. `"Internal server error retrieving parent workflow jobs"` / `"Internal server error retrieving ingested repositories"`).
- Upgrade logging to capture the full traceback internally — use `logger.exception(...)` or `logger.error(..., exc_info=True)` instead of the current `logger.error("...: {}", str(e))` which only logs the string representation.
- Ensure no internal error details reach the client in the 500 response body.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The HTTPException raised in get_parent_workflow_jobs uses a generic detail string (no str(e) interpolation)
- [ ] #2 The HTTPException raised in get_ingested_repositories uses a generic detail string (no str(e) interpolation)
- [ ] #3 Both exception handlers log the full traceback using logger.exception() or logger.error with exc_info=True
- [ ] #4 A 500 response body from either endpoint contains only the generic message, not internal error details
<!-- AC:END -->
