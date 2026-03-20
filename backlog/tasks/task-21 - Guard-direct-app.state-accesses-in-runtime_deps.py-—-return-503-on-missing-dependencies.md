---
id: TASK-21
title: >-
  Guard direct app.state accesses in runtime_deps.py — return 503 on missing
  dependencies
status: To Do
assignee: []
created_date: '2026-03-19 13:33'
labels:
  - hardening
  - flow-bridge
  - fastapi
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/utility/runtime_deps.py
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**File**: `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/utility/runtime_deps.py` (lines 12–27)

**Problem**: The three FastAPI dependency functions (`get_env_settings`, `get_temporal_client_dep`, `get_codebase_detectors`) access `request.app.state.<attr>` without any guard. If a startup event fails to wire a dependency, the request handler produces an uncontrolled `AttributeError` → generic 500 instead of a meaningful error.

**Required change**: In each function, verify that `request.app` and `request.app.state` exist and that the expected attribute is present **and** of the expected type:

| Function | Attribute | Expected type |
|---|---|---|
| `get_env_settings` | `code_confluence_env` | `EnvironmentSettings` |
| `get_temporal_client_dep` | `temporal_client` | `Client` |
| `get_codebase_detectors` | `codebase_detectors` | `dict[str, CodebaseDetector]` |

If any check fails, raise `HTTPException(status_code=503)` with an actionable `detail` message indicating which runtime dependency is missing (e.g., `"EnvironmentSettings not wired: code_confluence_env missing from app.state"`).

**Important**: Before implementing, verify each finding against the current code and only fix what is actually needed — the functions may already have been partially guarded in the interim.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each of the three functions checks that the expected attribute exists on `request.app.state` and is of the correct type before returning it
- [ ] #2 Missing or wrong-typed attribute raises `HTTPException(status_code=503)` with an actionable detail message naming the missing dependency
- [ ] #3 No existing passing tests are broken by the change
- [ ] #4 New or updated unit tests cover the 503 path for each function (attribute missing, wrong type)
- [ ] #5 Type-check passes (`basedpyright`) and linter passes (`ruff check`)
<!-- AC:END -->
