---
id: TASK-4.5
title: >-
  TASK-4 follow-up hardening: configurable tool result cap + modal
  resilience/performance
status: To Do
assignee: []
created_date: '2026-03-03 07:10'
updated_date: '2026-03-19 09:57'
labels:
  - backend
  - frontend
  - performance
  - reliability
  - ux
dependencies:
  - TASK-4.4
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/event_stream_handler.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/config/settings.py
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/ToolDetailModal.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventsAccordion.tsx
  - unoplat-code-confluence-frontend/src/routes/__root.tsx
parent_task_id: TASK-4
priority: high
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context
Post-implementation review identified reliability and performance gaps in the Live Tool Events flow.

## Validation findings
- Backend truncation cap is currently hardcoded in `event_stream_handler.py` as `[:100_000]` with no configuration hook.
- Frontend Tool Detail modal currently renders full result content directly in a `<pre>` block, which can receive up to the backend cap size.
- The frontend route/component tree does not currently define an explicit React error boundary around the new modal flow.

## Goal
Harden Flow 2 so tool-result handling is configurable, resilient to rendering failures, and performant for large payloads while preserving full-result access and copy behavior.

## Scope
- Backend: replace hardcoded tool result cap with environment-configurable setting (default remains current behavior).
- Frontend: add failure containment for modal rendering and improve large-content rendering strategy.
- Preserve existing Flow 1/Flow 2 behavior and strict `tool_call_id` pairing.

## Out of scope
- Changing event pairing semantics.
- Redesigning the Flow 1/Flow 2 visual system beyond resilience/performance fixes.

## Suggested implementation directions
- Use a typed environment setting for tool result max chars (validated bounds + safe fallback).
- Add a dedicated error boundary around Tool Detail modal content with a non-breaking fallback UI.
- Apply lazy rendering and/or virtualized/chunked rendering for large tool results; keep copy action for full content.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tool result truncation cap is configurable via environment variable with default value equal to current production behavior (100000 chars).
- [ ] #2 Invalid or unsafe cap values are validated/guarded, and backend behavior remains deterministic.
- [ ] #3 Tool Detail modal failures are isolated by an explicit error boundary so the surrounding events UI remains usable.
- [ ] #4 Large tool-result payloads use a bounded rendering strategy (lazy mount and/or virtualized/chunked rendering) to avoid UI lockups while preserving full-content copy action.
- [ ] #5 Flow 1 and Flow 2 interaction behavior remains unchanged functionally after hardening.
- [ ] #6 Quality checks pass for touched areas (backend typecheck/lint/tests and frontend lint/build).
<!-- AC:END -->
