---
id: TASK-12
title: Add cancel action for agent workflows in Operations Management
status: Done
assignee: []
created_date: '2026-03-10 09:28'
updated_date: '2026-03-19 09:57'
labels:
  - operations-management
  - agent-md
  - cancellation
  - frontend
  - query-engine
  - ingestion
dependencies: []
references:
  - >-
    unoplat-code-confluence-frontend/src/components/custom/SubmittedJobsDataTable.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsDialog.tsx
  - unoplat-code-confluence-frontend/src/components/custom/JobStatusDialog.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/submitted-jobs-data-table-columns.tsx
  - unoplat-code-confluence-frontend/src/lib/api.ts
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/workflow_service.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_models.py
documentation:
  - 'https://python.temporal.io/temporalio.client.WorkflowHandle.html'
  - 'https://docs.temporal.io/develop/python'
priority: high
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Users need a way to stop a running AGENTS.md workflow from Operations Management. The cancel control must be available only for AGENTS_GENERATION and AGENT_MD_UPDATE runs, and must never be shown for INGESTION runs. This spans query-engine (cancel API + Temporal workflow cancellation), ingestion (job-list contract support for cancellability gating), and frontend (Operations Management action wiring and UX states).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Operations Management allows user-initiated cancellation for in-flight AGENTS_GENERATION and AGENT_MD_UPDATE runs.
- [ ] #2 Operations Management never displays a cancel action for INGESTION runs.
- [ ] #3 Query-engine provides a cancel endpoint that accepts repository owner/name/run identifier and returns deterministic responses for success, non-cancellable operation, not-found run, and already-terminal run.
- [ ] #4 Query-engine uses Temporal Python async cancellation (`await handle.cancel()`) for workflow cancellation.
- [ ] #5 Cancellation behavior does not require introducing a new workflow status enum value; existing status model remains valid and cancellation context is preserved in error/report metadata.
- [ ] #6 Frontend shows pending/disabled state during cancel request, then refreshes operations data and shows success or error feedback.
- [ ] #7 Ingestion job-list API provides enough data to gate cancel visibility safely in UI (existing operation/status fields or explicit cancellable flag).
- [ ] #8 Relevant API/docs/tests are updated to reflect the cancel workflow behavior and ingestion exclusion rule.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Scope
Enable Operations Management users to stop a running AGENTS.md workflow while guaranteeing that ingestion workflows never expose or accept cancellation.

## Implementation Plan
1. Query-engine cancellation API
- Add a dedicated endpoint in `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py` for repository agent run cancellation.
- Request contract: repository owner, repository name, repository workflow run id.
- Validate target run from `RepositoryWorkflowRun` (owner/name/run tuple).
- Enforce operation guardrail: reject `INGESTION` at API layer even if called directly.
- Enforce state guardrail: reject already-terminal runs (COMPLETED/FAILED/TIMED_OUT/ERROR) with deterministic response.
- Use Temporal async handle cancellation (`client.get_workflow_handle(...); await handle.cancel()`).
- Normalize Temporal RPC failures into stable API responses (not found, invalid state, generic failure).

2. Cancellation status behavior
- Keep current `JobStatus` enum unchanged (no new `CANCELLED` status in this increment).
- Persist cancellation context via error metadata/report path (e.g., source=user_action, reason=cancel_requested) so UI and diagnostics can distinguish manual stop from runtime failures.
- Ensure eventual status transition after cancel request remains compatible with existing interceptors and terminal-state handling.

3. Ingestion job-list contract alignment
- Update ingestion `/parent-workflow-jobs` response model and mapper to include explicit cancellability signal derived from operation + status (or formally document operation/status gating if explicit field is skipped).
- Rule: only AGENTS_GENERATION / AGENT_MD_UPDATE can be cancellable; INGESTION is always false.

4. Frontend Operations Management wiring
- Add query-engine API client method for cancel action in `unoplat-code-confluence-frontend/src/lib/api.ts`.
- Extend job typing to carry cancellability signal in `unoplat-code-confluence-frontend/src/types.ts`.
- Add cancel CTA to AGENTS dialog flow in `unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsDialog.tsx` only when run is cancellable and in-flight.
- Do not add cancel CTA in ingestion details dialog (`JobStatusDialog`).
- Add loading/disabled UX, success/failure toast, and query invalidation (`parentWorkflowJobs`, and any active run detail queries) after action.

5. Verification and docs
- Add/adjust backend tests for cancel endpoint guards and success path.
- Add/adjust ingestion API tests for cancellability field derivation.
- Add/adjust frontend tests (or documented manual validation) for agent-only cancel visibility.
- Update interface docs where applicable (`app_interfaces.md` in touched services).

## Delivery Notes
- Cancellation request acknowledgement does not guarantee immediate workflow termination; UI should reflect "cancel requested" semantics until a terminal status is observed.
- Backend enforcement is mandatory so ingestion cannot be cancelled even if a client bypasses UI controls.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Design Decisions Captured
- FastAPI endpoint is async; Temporal cancellation must use async call with `await handle.cancel()`.
- No new workflow status enum is introduced in this increment to avoid cross-service schema/constraint migration blast radius.
- Ingestion exclusion is enforced in both layers: UI visibility rules and backend API validation.

## Files and Surfaces to Touch
- Query-engine endpoint and Temporal interaction: `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`
- Ingestion operations list contract: `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/main.py`, `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py`
- Frontend operation UX/API/types: `unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsDialog.tsx`, `unoplat-code-confluence-frontend/src/components/custom/JobStatusDialog.tsx`, `unoplat-code-confluence-frontend/src/components/custom/SubmittedJobsDataTable.tsx`, `unoplat-code-confluence-frontend/src/lib/api.ts`, `unoplat-code-confluence-frontend/src/types.ts`

## Operational Guardrails
- Reject cancel attempts when operation is `INGESTION`.
- Reject cancel attempts for terminal statuses.
- Return deterministic API messages for: run not found, already terminal, non-cancellable operation, cancel accepted, and backend failure.

Implementation started in this session.

Implemented query-engine cancel endpoint `POST /v1/repository-agent-run/cancel` with operation guardrails (agent-only), terminal-state guardrails, async Temporal cancel (`await handle.cancel()`), and deterministic HTTP responses for not found/non-cancellable/already-terminal/runtime unavailable.

Implemented ingestion operations-list cancellability contract by adding `is_cancellable` to `ParentWorkflowJobResponse` and deriving it in `/parent-workflow-jobs` from operation + status.

Implemented frontend wiring: added `cancelRepositoryAgentRun()` API client, added `is_cancellable` in `ParentWorkflowJobResponse` type, and added Cancel Run action in `GenerateAgentsDialog` for in-flight agent workflows only (not ingestion dialog).

Updated interface documentation in query-engine and ingestion `app_interfaces.md`.

Verification run: frontend `bun run build` passed. Targeted query-engine typecheck for modified endpoint passed. Targeted ingestion typecheck for modified model passed. Full-repo Python typechecks in query-engine/ingestion still report many pre-existing unrelated issues.

Created child task `TASK-12.1` to address UX guardrail for preventing concurrent AGENTS.md run starts for the same repository.

Simplified cancellation implementation per alpha scope: removed legacy/backward-compatibility recovery path and enforced strict workflow-id semantics. `repository_workflow_id` is now required at workflow-run initialization and DB activity raises if workflow_id is missing.

Manual retest still resulted in `COMPLETED` after cancel. Continuing investigation into workflow cancellation propagation paths inside query-engine Temporal workflows.

Used Temporal CLI on workflow `agent-fastapi-full-stack-fastapi-template-62517836` / run `019ce18e-5464-747b-a3a7-50aaa7fc8175` to confirm exact propagation bug: Temporal history ends in `WORKFLOW_EXECUTION_CANCELED`, but our interceptor scheduled parent DB status `COMPLETED` just before close. Root cause was repository interceptor not catching `asyncio.CancelledError` (inherits `BaseException`, not `Exception` in Python 3.13).

Implemented precise fix: cancellation helpers now recognize both Temporal `CancelledError` and `asyncio.CancelledError`, and repository/codebase interceptor execute-workflow wrappers now explicitly catch `asyncio.CancelledError` so final DB status is written as `CANCELLED` instead of defaulting to `COMPLETED`.

Refactored cancellation propagation logic to shared helper module `services/temporal/cancellation_helpers.py` to remove duplicated cause-chain parsing across workflow/interceptor.

`temporal_workflows.py` now imports shared `is_temporal_cancellation_exception` and keeps only `_raise_if_temporal_cancellation` wrapper for workflow-local logging.

`agent_workflow_interceptor.py` now imports the shared helper and uses `WORKFLOW_EXECUTION_EXCEPTIONS` constant to avoid duplicated except tuples.

Added targeted tests `tests/services/test_cancellation_helpers.py` for direct Temporal cancel, direct asyncio cancel, wrapped cancel chain, and non-cancel exception.

Verification: basedpyright (targeted files) passed; ruff check passed; pytest `tests/services/test_cancellation_helpers.py` passed (4 tests).
<!-- SECTION:NOTES:END -->
