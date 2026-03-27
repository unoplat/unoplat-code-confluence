---
id: TASK-3.6.3
title: >-
  Add structured CallExpression provenance and ambiguity metadata to framework
  definitions
status: To Do
assignee: []
created_date: '2026-03-07 04:54'
updated_date: '2026-03-19 09:57'
labels:
  - framework-detection
  - call-expression
  - schema
  - validator
dependencies:
  - TASK-3.6.2
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py
  - unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema.json
  - >-
    unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v3.json
documentation:
  - >-
    unoplat-code-confluence-query-engine/backlog/docs/doc-006 -
    CallExpression-Confidence-Scoring-and-Validation-Agent.md
parent_task_id: TASK-3.6
priority: high
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Introduce explicit contributor-authored metadata for `CallExpression` framework definitions so confidence calibration and validator behavior do not rely only on `base_confidence` plus freeform `notes`. The goal is to let contributors declare whether a call is a direct import-bound symbol match or whether it requires object provenance proof, and to describe the ambiguity class in a structured way that downstream loader/query-engine/validator flows can consume consistently.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CallExpression framework definitions support explicit structured metadata describing expected call binding shape and whether object provenance proof is required, instead of relying only on freeform notes.
- [ ] #2 Schema and typed contracts reject invalid or incomplete CallExpression provenance/ambiguity declarations and keep non-CallExpression concepts unchanged.
- [ ] #3 Loader/query-engine candidate payloads preserve the new structured CallExpression metadata so validator execution can consume it deterministically.
- [ ] #4 Validator prompting includes the structured provenance/ambiguity metadata and instructs the agent how to use it during docs-first review and decision-making.
- [ ] #5 Current shipped CallExpression framework definitions are updated with representative structured provenance/ambiguity metadata that matches their intended confidence level and validator needs.
- [ ] #6 Contributor documentation and targeted tests cover the new CallExpression metadata contract and expected validator behavior.
<!-- AC:END -->
