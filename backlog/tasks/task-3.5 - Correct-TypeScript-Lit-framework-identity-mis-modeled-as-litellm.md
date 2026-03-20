---
id: TASK-3.5
title: Correct TypeScript Lit framework identity mis-modeled as litellm
status: To Do
assignee: []
created_date: '2026-03-04 11:17'
updated_date: '2026-03-19 09:57'
labels:
  - framework-definitions
  - typescript
  - data-quality
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/litellm.json
  - >-
    unoplat-code-confluence-docs/public/framework-definitions/typescript/litellm.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/engine/programming_language/typescript/test_typescript_additional_concept_extraction.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_framework_definitions_ingestion.py
parent_task_id: TASK-3
priority: medium
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TypeScript framework definitions currently model Lit (`lit.dev`, `LitElement`, `@property/@state`) under the library key `litellm`, which is semantically incorrect and collides conceptually with the real Python `litellm` integration. This task renames the TypeScript framework identity to `lit` and aligns docs/tests so downstream reporting, interfaces, and analytics attribute detections correctly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 TypeScript framework definition key is `lit` (not `litellm`) while preserving current Lit feature semantics (`LitElement`, `property`, `state`).
- [ ] #2 Definition filenames and internal references are consistent (`lit.json` or equivalent canonical naming) in ingestion and docs directories.
- [ ] #3 TypeScript tests that currently assert library `litellm` are updated to assert `lit`, with no regressions in framework-definition ingestion tests.
- [ ] #4 Validation/check commands for framework definitions and targeted tests pass after the rename.
- [ ] #5 A short migration note is added in task notes/final summary describing the identity change and potential downstream data impact for historical rows.
<!-- AC:END -->
