---
id: TASK-3.3.1
title: Make CallExpression validator prompt metadata-aware and docs-first
status: Done
assignee: []
created_date: '2026-03-06 11:18'
updated_date: '2026-03-10 09:31'
labels:
  - query-engine
  - validator
  - prompting
  - call-expression
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py
parent_task_id: TASK-3.3
priority: high
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Improve the CallExpression validator agent instructions so the model is explicitly told which candidate payload fields and CallExpression metadata fields it receives, uses official documentation review before adjudication, then compares documentation expectations against detector metadata and local code evidence before persisting evidence/status.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Validator system prompt explicitly documents candidate payload fields available to the agent: identity, concept, match_confidence, validation_status, match_text, evidence_json, base_confidence, notes, construct_query, absolute_paths.
- [x] #2 Validator prompt/workflow explicitly documents expected CallExpression metadata keys that may appear in `evidence_json` (including `concept`, `source`, `match_confidence`, `call_match_kind`, `matched_absolute_path`, optional `matched_alias`, and `call_match_policy_version`).
- [x] #3 Required process is reordered so the agent reviews official documentation first, then compares docs expectations against candidate metadata and local code evidence before deciding.
- [x] #4 Prompt instructions explicitly tell the agent to record gaps/mismatches (for example import-binding mismatch, alias/path mismatch, API-shape mismatch, insufficient provenance) in evidence payloads before status transition.
- [x] #5 Targeted query-engine tests cover the new prompt content/sequence and pass.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-03-06: Started prompt-improvement slice. Scope: make validator system prompt and workflow prompt explicitly describe candidate payload fields, expected CallExpression evidence metadata keys, docs-first review order, and evidence gap recording requirements.

Updated `create_call_expression_validator_agent(...)` instructions to explicitly describe candidate payload fields, identity subfields, and expected CallExpression evidence_json keys (`concept`, `source`, `match_confidence`, `call_match_kind`, `matched_absolute_path`, optional `matched_alias`, `call_match_policy_version`, `callee`, `args_text`, `validator`).

Reordered validator instructions to a docs-first process: review official docs first, then read local file context, then expand nearby symbol/object evidence, then compare docs expectations against candidate metadata/evidence_json/local code before deciding.

Prompt now explicitly instructs the agent to record gaps/mismatches (import-binding mismatch, alias/path mismatch, API-shape mismatch, insufficient provenance, unsupported args/docs mismatch) in evidence_json before status transition.

Expanded workflow prompt builder so each candidate run includes a metadata guide, evidence_json key guide, docs-first review order, and evidence payload expectations.

Verification: `uv run --group dev basedpyright ...` passed, `uv run --group dev ruff check ...` passed, `uv run --group test pytest tests/services/test_call_expression_validator_prompting.py -v` passed (2 tests).
<!-- SECTION:NOTES:END -->
