---
id: TASK-3.7
title: >-
  Align validator progress naming and ordering with App Interfaces workflow in
  frontend
status: Done
assignee: []
created_date: '2026-03-07 12:38'
updated_date: '2026-03-10 09:31'
labels:
  - frontend
  - progress-ui
  - validator
  - app-interfaces
dependencies: []
references:
  - unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventsAccordion.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/GenerateAgentsProgress.tsx
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
documentation:
  - Logfire trace 019cc6b086da24fda466c36da3475f50
  - 'backlog://workflow/overview'
parent_task_id: TASK-3
priority: high
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Improve the workflow progress UI so low-confidence CallExpression validation is presented in user-friendly terms and appears in the same sequence as the actual workflow. Logfire investigation for trace `019cc6b086da24fda466c36da3475f50` confirmed the backend order is already correct for the App Interfaces stage: validator runs before the `## App Interfaces` section updater, but the frontend currently renders the unknown agent id `call_expression_validator` using a fallback title (`Call Expression Validator`) and sorts it last. This task is the frontend-first fix: register the validator as a first-class progress group with intuitive naming such as `App Interface Validator`, give it an explicit order before `App Interfaces`, and preserve grouping behavior for related updater events and historical traces. Backend agent-id renaming can be handled in a later follow-up if still desired.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Frontend agent grouping registers the current validator event key (`call_expression_validator`) as a first-class known agent instead of relying on snake_case fallback display formatting.
- [x] #2 The progress UI shows an intuitive label for validator work (for example `App Interface Validator`) rather than `Call Expression Validator`.
- [x] #3 The validator group sorts before `App Interfaces` so the codebase progress list reflects the real workflow order for the app-interfaces stage.
- [x] #4 Existing display/grouping behavior for `app_interfaces_agent` and `app_interfaces_agents_md_updater` remains intact.
- [x] #5 Historical runs that still emit `call_expression_validator` render correctly without requiring backend changes.
- [x] #6 Frontend verification covers display-name resolution and ordering behavior for validator + app-interfaces agent groups.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1) Promote the validator event key to a first-class frontend agent.
- Add a dedicated agent constant/registry entry for `call_expression_validator` in `src/lib/agent-events-utils.ts`.
- Give it a user-facing display name such as `App Interface Validator`.
- Assign it an explicit order immediately before `app_interfaces_agent`.

2) Preserve existing grouping semantics for App Interfaces.
- Keep `app_interfaces_agent` as the canonical group for App Interfaces output.
- Keep `app_interfaces_agents_md_updater` aliased to `app_interfaces_agent` so the updater remains grouped under App Interfaces.
- Do not alias `call_expression_validator` into `app_interfaces_agent`; it should appear as its own explicit progress row.

3) Add focused frontend verification.
- Add unit coverage around display-name resolution and sorting/grouping behavior in `agent-events-utils`.
- Verify mixed event sets containing `call_expression_validator`, `app_interfaces_agent`, and `app_interfaces_agents_md_updater` produce the expected group labels and order.

4) Validate in the frontend workspace.
- Run frontend type/build verification first, then lint, on the touched files.
- Confirm the progress accordion renders the new label/order without requiring backend event-id changes.

5) Follow-up note.
- If product still wants backend/logfire/internal IDs renamed after this lands, create a separate follow-up so historical event compatibility remains explicit rather than bundled into the frontend-only fix.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Logfire evidence used for this task: in trace `019cc6b086da24fda466c36da3475f50`, `call_expression_validator run` begins at 2026-03-07T05:11:35Z, while the `## App Interfaces` `agents_md_updater run` begins later at 2026-03-07T05:13:08Z. This confirms the apparent mis-order in the UI is caused by frontend fallback naming/sort behavior rather than backend execution order.

Current frontend root cause: `src/lib/agent-events-utils.ts` does not register `call_expression_validator` in `AgentType` / `AGENT_REGISTRY`, so `getAgentDisplayName()` falls back to snake_case titleization and `getAgentOrder()` falls back to 999, pushing the validator row to the end of the accordion.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Registered `call_expression_validator` as a first-class frontend agent in `unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts` and gave it the user-facing label `App Interface Validator`.

Assigned the validator an explicit order before `app_interfaces_agent` and kept `app_interfaces_agents_md_updater` grouped under App Interfaces. Added a forward-compatible alias from `app_interface_validator` to `call_expression_validator` for future backend renaming.

Verified the change with frontend TypeScript/build checks, targeted ESLint on the updated file, and an ad-hoc Bun assertion that `call_expression_validator` now renders before `app_interfaces_agent` with the expected display names.
<!-- SECTION:FINAL_SUMMARY:END -->
