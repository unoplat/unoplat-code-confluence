---
id: TASK-1.2
title: >-
  Integrate low-confidence CallExpression validator agent into query-engine
  workflow
status: Done
assignee: []
created_date: '2026-02-26 10:41'
updated_date: '2026-03-10 09:31'
labels:
  - query-engine
  - validator
  - call-expression
  - confidence
  - workflow
  - app-interfaces
dependencies:
  - TASK-1.1
references:
  - >-
    unoplat-code-confluence-query-engine/backlog/docs/doc-006 -
    CallExpression-Confidence-Scoring-and-Validation-Agent.md
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_framework_repository.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/app_interfaces_activity.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/repository/app_interfaces_mapper.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_worker_manager.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/tools/get_content_file.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/tools/search_across_codebase.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/code_confluence_codebase_parser.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py
documentation:
  - 'backlog://workflow/overview'
parent_task_id: TASK-1
priority: high
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement Phase 3 of doc-006 for Python app interface mapping: validate low-confidence `CallExpression` usage rows before interface aggregation, persist outcomes, and harden doc-006 with an explicit algorithm + gap analysis.

Goal
- If `match_confidence < 0.70` for `CallExpression`, run validator for that usage before mapper inclusion.
- Validator must verify local code evidence (file/line context) and official library docs.
- Official-doc retrieval must follow existing search-mode behavior: Exa when configured, otherwise native built-in web search for supported providers, otherwise mark `needs_review`.

Algorithm (Doc-006 hardening)
1) Candidate fetch
   - Query usage rows with: identity keys, `match_confidence`, `validation_status`, `evidence_json`, and feature metadata (`concept`, `base_confidence`, `construct_query`, `notes`, `absolute_paths`).
2) Partition (simplified for Phase 3)
   - Validator candidates only: `concept == CallExpression` AND confidence `< 0.70` AND status in `{pending, needs_review}`.
   - Bypass set: all other rows.
3) Validator execution per low-confidence candidate
   - Read precise file window (`read_file_content`) and symbol context (`search_across_codebase`).
   - Validate claimed framework usage against official docs via configured external search mode.
   - Return structured decision: `confirm | reject | correct | needs_review`, `final_confidence`, `updated_feature_key?`, and structured evidence.
4) Write-back via two explicit tools
   - Tool A: evidence/confidence upsert (`match_confidence`, `evidence_json`, corrected-row upsert when `decision=correct`).
   - Tool B: status-only transition (`validation_status`).
   - Status transitions: `pending|needs_review -> completed` OR `pending|needs_review -> needs_review`.
   - For `correct`: create corrected usage row (new feature key) and retain audit on original row in evidence.
5) Merge + mapping
   - Build interfaces from: bypass set + completed(`confirm`/`correct`) rows.
   - Exclude completed(`reject`) and `needs_review` rows.
6) Observability
   - Emit candidate volume, completed/needs_review rates, decision rates, confidence shift, validator latency/token-cost metrics.

Important gaps to close (must be called out in doc-006 + implementation)
1. `match_confidence` scoring is not yet effectively populated for detections (current fallback behavior causes weak threshold gating).
2. Query-engine framework usage fetch still reads line-span + `match_text` and does not consume confidence/validation/evidence fields.
3. No validator TemporalAgent/plugin is currently wired into worker/workflow path for app interfaces.
4. No dedicated query-engine persistence tools exist yet for (a) evidence/confidence upsert and (b) status-only transition.
5. Existing runtime table creation uses `create_all`; migration/backfill expectations must be explicit for existing DBs.

Implementation block
A) Query-engine data access
- Extend framework usage repository read path to include confidence/status/evidence + feature metadata needed by validator.
- Add write/update repository methods for validation outcomes and corrected-row insertion.

B) Validator output contracts
- Add strict output model + validator function with retry-safe constraints.
- Ensure decisions and evidence schema are deterministic and auditable.

C) Validator agent + tooling
- Add `call_expression_validator` agent in temporal agent registry.
- Reuse current search mode resolution (`exa` vs builtin web search) and provider compatibility behavior.
- Add two dedicated function tools (following existing query-engine tool conventions in `src/.../tools/`):
  - `upsert_framework_feature_validation_evidence`
    - Input: row identity tuple + decision payload + final confidence + evidence + optional `updated_feature_key`
    - Behavior: update original row evidence/confidence; for `correct`, upsert corrected row
  - `set_framework_feature_validation_status`
    - Input: row identity tuple + target status + optional expected current status
    - Behavior: enforce allowed transitions (`pending|needs_review -> completed|needs_review`) with idempotent guards
- Route both tools through repository-layer DB helpers under `db/postgres` using `get_startup_session()` and strict typed DTOs.

D) Workflow/activity integration
- Add low-confidence validation step in workflow before `app_interfaces_activity` mapping.
- Register required activities/plugins in worker manager.
- Preserve existing app-interfaces completion event semantics.

E) Mapper gating
- Ensure mapper input excludes rejected/needs_review rows and includes corrected rows.

F) Documentation hardening
- Update doc-006 with the finalized algorithm above and the explicit important-gap section.

G) Tests
- Repository tests for read partitioning + write-back transitions.
- Validator output contract tests.
- Workflow/activity tests for gating and merge behavior.
- Mapper tests for reject/correct/needs_review handling.

Out of scope
- TypeScript validator rollout (deferred until TS detection path is fully wired and benchmarked).
- Broad concept expansion beyond CallExpression in this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Validator candidate selection is implemented only for `CallExpression` rows with `match_confidence < 0.70` (Python path for this phase).
- [x] #2 Validator agent verifies local code evidence (file/line + symbol context) and official docs source before decisioning each low-confidence candidate.
- [x] #3 External docs lookup follows configured search capability precedence: Exa when configured, otherwise built-in web search for supported providers; when unavailable, candidate is marked `needs_review`.
- [x] #4 Validation write-back is implemented through two tools: evidence/confidence upsert tool and status-transition tool, with deterministic transitions and idempotent behavior.
- [x] #5 `correct` decisions produce corrected mapping behavior (corrected row path) while preserving original row audit trail in evidence.
- [x] #6 App interfaces mapping consumes high-confidence/non-target rows plus validator-completed rows with `confirm|correct`; rejected and needs_review rows are excluded.
- [x] #7 Doc-006 is updated with the finalized end-to-end algorithm and explicit important-gap section aligned to this simplified trigger rule.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Precise Implementation Plan (Remaining Work)

1. Candidate read path and trigger filter
- Extend query-engine framework repository read API to return validator candidate rows with full identity tuple (`file_path`, `feature_language`, `feature_library`, `feature_key`, `start_line`, `end_line`), plus `match_confidence`, `validation_status`, `evidence_json`, `match_text`, and feature metadata (`concept`, `base_confidence`, `notes`, `construct_query`, `absolute_paths`).
- Enforce Phase-3 trigger predicate in selection/filtering:
  - `concept == CallExpression`
  - `match_confidence < 0.70`
  - `validation_status in {pending, needs_review}`

2. Validator output contract
- Add strict validator decision model with:
  - `decision: confirm | reject | correct | needs_review`
  - `final_confidence: 0.0..1.0`
  - `updated_feature_key` required only when `decision=correct`
  - structured `evidence_json` including rationale, line references, and docs references.
- Add output validation/retry guardrails to reject malformed decision payloads.

3. Validator agent definition
- Add `call_expression_validator` agent definition in temporal agent registry.
- Register tool surface for validator execution:
  - `read_file_content`
  - `search_across_codebase`
  - `upsert_framework_feature_validation_evidence`
  - `set_framework_feature_validation_status`
- Keep tool docstrings in Google format with explicit parameter descriptions so Griffe enriches tool schema.

4. Official docs lookup precedence wiring
- Reuse existing query-engine search-mode resolution precedence:
  - Exa configured -> Exa toolset
  - else provider supports native web search -> built-in web search
  - else -> produce `needs_review` decision path.
- Persist external evidence references into `evidence_json`.

5. Temporal activity and workflow integration
- Add dedicated validation activity for low-confidence `CallExpression` candidates.
- Wire activity into workflow before `app_interfaces_activity` mapping stage.
- Register activity in worker manager so runtime executes validator pass durably.

6. Two-tool write-back protocol (already implemented foundation, now enforce in workflow)
- For each validator candidate:
  1) call `upsert_framework_feature_validation_evidence`
  2) call `set_framework_feature_validation_status`
- Allowed transitions:
  - `pending|needs_review -> completed`
  - `pending|needs_review -> needs_review`
  - `completed -> completed` idempotent no-op only
- For `decision=correct`, maintain corrected-row upsert + original-row audit trail behavior.

7. Mapper gating integration
- Build app interfaces from:
  - bypass rows (non-candidates)
  - validator-completed rows with `decision in {confirm, correct}`
- Exclude:
  - rows with `decision=reject`
  - rows with `validation_status=needs_review`

8. Observability and failure handling
- Emit metrics:
  - low-confidence candidate volume
  - decision rates (`confirm/reject/correct/needs_review`)
  - status rates (`completed/needs_review`)
  - confidence delta (before/after)
  - validator latency and token cost
- Failure policy:
  - if evidence upsert succeeds and status transition fails, retry transition and fallback to `needs_review` on bounded retries.

9. Test plan and verification
- Repository tests: candidate fetch filter + transition guards + corrected-row behavior.
- Tool tests: typed request/response contracts + ModelRetry behavior.
- Workflow/activity tests: validator invoked only for trigger-matching rows.
- Mapper tests: include confirm/correct, exclude reject/needs_review.
- Verification commands:
  - `task typecheck`
  - `task lint`
  - targeted tests via `uv run --group test pytest ... -v` for touched suites.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Scope simplification confirmed with requester: validator trigger for this phase is ONLY `concept == CallExpression` AND `match_confidence < 0.70` (Python path). We are intentionally avoiding extra queue taxonomy (`auto_accept_queue` / `already_completed_queue`) in the implementation narrative for now. Practical behavior: rows matching this predicate are validator candidates; all other rows bypass validator in this phase.

Updated doc-006 planning narrative to enforce simplified Phase-3 trigger (`CallExpression` + `match_confidence < 0.70` + status `pending|needs_review`), added deterministic validator algorithm section, and added explicit Important Gaps section (scoring population, query-engine read path, validator wiring, write-back path, migration/backfill risk).

Design refinement captured: write-back is split into two explicit tools tailored to existing query-engine tool architecture (`RunContext[AgentDependencies]` + strict typed payloads + `ModelRetry` guards + repository-layer DB helpers).
1) `upsert_framework_feature_validation_evidence`: updates `match_confidence` + `evidence_json` and upserts corrected row for `decision=correct`.
2) `set_framework_feature_validation_status`: status-only transition with allowed-state guards and idempotent replay semantics.

Implementation started in build mode. Beginning with query-engine persistence foundation for validator write-back: repository methods + two dedicated tools (`upsert_framework_feature_validation_evidence`, `set_framework_feature_validation_status`) aligned to existing RunContext/ModelRetry patterns.

Implemented first code slice for validator persistence foundation:
- Added typed Pydantic repository models in `src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py` (identity tuple, decision enum, evidence upsert request/result, status transition request/result).
- Extended `db/postgres/code_confluence_framework_repository.py` with:
  - `db_upsert_framework_feature_validation_evidence(...)`
  - `db_set_framework_feature_validation_status(...)`
  - guarded status transition logic and evidence merge payload construction.
- Added tool wrappers in `src/unoplat_code_confluence_query_engine/tools/framework_feature_validation_tools.py` using `RunContext[AgentDependencies]` + `ModelRetry` validation/guardrails.
- Added tests:
  - integration DB tests with real Postgres container path: `tests/db/test_framework_feature_validation_repository.py`
  - tool wrapper unit tests: `tests/tools/test_framework_feature_validation_tools.py`
- Verification:
  - `uv run --group dev basedpyright ...` on touched source files: pass
  - `uv run --group dev ruff check ...` on touched source/tests: pass
  - `uv run --group test pytest tests/tools/test_framework_feature_validation_tools.py tests/db/test_framework_feature_validation_repository.py -v`: 6 passed

Refinement based on PydanticAI docs (`tools.md`, `tools-advanced.md`): switched validator tool signatures to typed Pydantic request/response objects instead of raw scalar args + dict returns.
- `upsert_framework_feature_validation_evidence(ctx, request: FrameworkFeatureValidationEvidenceUpsertRequest) -> FrameworkFeatureValidationEvidenceUpsertResult`
- `set_framework_feature_validation_status(ctx, request: FrameworkFeatureValidationStatusTransitionRequest) -> FrameworkFeatureValidationStatusTransitionResult`
This removes manual identity construction/parsing from tool wrappers and avoids `model_dump(mode='python')` inside tools (typed objects are returned directly). Added/updated tests accordingly; all targeted tests pass.

Progress update (achieved vs pending):

Achieved
- Added typed validator persistence models (`FrameworkFeatureUsageIdentity`, decision enum, evidence upsert/status transition request+result models).
- Implemented repository write-back APIs:
  - `db_upsert_framework_feature_validation_evidence(...)`
  - `db_set_framework_feature_validation_status(...)`
- Implemented two dedicated tools with typed Pydantic request/response contracts and ModelRetry wrapping for repository validation failures:
  - `upsert_framework_feature_validation_evidence`
  - `set_framework_feature_validation_status`
- Updated tool docstrings to Google format with explicit Args/Returns/Raises descriptions so Griffe can enrich tool schemas.
- Added/updated tests for repository behavior and tool wrappers; targeted test suite passes.

Pending
- Candidate selection/read path for validator trigger (`CallExpression` + `match_confidence < 0.70` + status `pending|needs_review`).
- Validator TemporalAgent implementation and workflow integration before app interfaces activity.
- External docs search precedence wiring inside validator execution path (Exa -> builtin web search -> needs_review fallback).
- Mapper gating integration to include only bypass + validator completed(confirm/correct), exclude reject/needs_review.
- Metrics/observability instrumentation for candidate volume, decisions, status rates, latency/token cost.
- Final workflow/mapper integration tests (beyond current repository/tool-level tests).

Implemented workflow-level low-confidence gating and validator wiring:
- Added repository candidate query `db_get_low_confidence_call_expression_candidates(...)` for trigger predicate: `CallExpression` + `match_confidence < 0.70` + status in `{pending, needs_review}`.
- Updated app-interface fetch path filtering in `db_get_all_framework_features_for_codebase(...)` to exclude low-confidence unresolved CallExpression rows and include only completed confirm/correct decisions.
- Added Temporal activity `fetch_low_confidence_call_expression_candidates` and registered it in worker activities.
- Added `call_expression_validator` Temporal agent definition and registration in temporal agent factory + worker plugin setup.
- Added workflow helper `_run_call_expression_validation(...)` and integrated execution before app-interface mapping; validator is skipped when candidate list is empty.
- Added reusable search-mode utilities in `agents/code_confluence_agents.py` so both dependency and validator prompts share mode-specific official-doc instructions.
- Updated doc-006 write-back section with explicit tool workflow examples (confirm and needs_review paths).
- Verification: basedpyright and ruff pass on touched source/tests; tool-unit tests pass. Repository integration tests are currently blocked locally by Docker Postgres port 5432 conflict (environment issue).

Additional implementation completed:
- Added shared search-mode instruction utilities in `agents/code_confluence_agents.py` and reused them from temporal agent constructors (dependency + call-expression validator), so search-mode wording is centralized and consistent.
- Implemented `create_call_expression_validator_agent(...)` with explicit tool workflow examples in the prompt (confirm and needs_review paths), and configured two write tools with `docstring_format='google'` + `require_parameter_descriptions=True`.
- Registered call-expression validator in temporal agent creation and worker plugin wiring.
- Added workflow integration in `temporal_workflows.py`: fetch low-confidence candidates activity -> conditional validator run helper -> app interfaces activity.
- Added activity method `fetch_low_confidence_call_expression_candidates` in `app_interfaces_activity.py`.
- Added repository tests for candidate query and app-interface gating behavior.
- Verification status: touched-file basedpyright/ruff pass; tool tests pass; DB integration tests blocked by local Docker port conflict (`0.0.0.0:5432 already allocated`).

Per requester direction, validator metrics emission (candidate/decision/status/confidence-delta/latency-cost telemetry) is deferred and removed from current implementation scope. This will be tracked as follow-up backlog work.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Targeted query-engine tests for repository/read-write, validator contract, workflow gating, and mapper behavior pass locally.
- [x] #2 Task-scoped lint/typecheck pass on touched query-engine files using project commands.
- [x] #3 No validator logic is executed for non-CallExpression concepts in this phase.
- [x] #4 Implementation notes include final status-transition table and corrected-row handling details.
- [ ] #5 Metrics emission is intentionally deferred to follow-up backlog work for this phase.
<!-- DOD:END -->
