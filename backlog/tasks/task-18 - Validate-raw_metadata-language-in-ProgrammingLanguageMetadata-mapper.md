---
id: TASK-18
title: 'Validate raw_metadata["language"] in ProgrammingLanguageMetadata mapper'
status: To Do
assignee: []
created_date: '2026-03-19 13:29'
labels:
  - flow-bridge
  - robustness
  - verify-first
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/repository/mappers.py
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/repository/mappers.py` around lines 31–37, the mapper that constructs `ProgrammingLanguageMetadata` accesses `raw_metadata["language"]` directly. If the key is missing, this raises an uncaught `KeyError`, which is opaque and hard to debug for callers.

Verify this finding against the current code and only fix it if needed. The mapper should validate that `"language"` exists in `raw_metadata` before building the object and raise a clear, explicit exception (e.g., `ValueError` with a message like `"missing required 'language' in raw_metadata"`) or provide a sensible default if appropriate. Optional fields should continue using `raw_metadata.get(...)` as before.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Verify the current code at the identified location actually has the unguarded raw_metadata["language"] access — only proceed with a fix if confirmed
- [ ] #2 If confirmed: add an explicit check for the "language" key in raw_metadata before constructing ProgrammingLanguageMetadata
- [ ] #3 If confirmed: raise a ValueError with a descriptive message (e.g. "missing required 'language' in raw_metadata") when the key is absent, OR provide a justified default
- [ ] #4 Optional fields in ProgrammingLanguageMetadata continue to use raw_metadata.get(...) with their existing defaults
- [ ] #5 Existing tests still pass; add or update a test covering the missing-key scenario
<!-- AC:END -->
