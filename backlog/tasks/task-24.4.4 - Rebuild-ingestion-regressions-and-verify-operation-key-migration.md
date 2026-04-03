---
id: TASK-24.4.4
title: Rebuild ingestion regressions and verify operation-key migration
status: In Progress
assignee:
  - '@OpenCode'
created_date: '2026-03-30 13:15'
updated_date: '2026-04-03 04:55'
labels:
  - ingestion
  - framework-features
  - tests
  - verification
milestone: Framework feature architecture
dependencies:
  - TASK-24.4.3
references:
  - TASK-24.4
  - doc-3
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_framework_definitions_ingestion.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/integration/test_framework_detection_with_postgres.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/parser/test_framework_detection_language_processor.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/engine/programming_language/typescript/test_nextjs_extraction.py
parent_task_id: TASK-24.4
priority: high
ordinal: 1540
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Focused loader, query, parser, and integration regressions already pass for the migrated operation-key corpus, but final migration verification and bookkeeping are still open. Confirm the required verification order, record any residual downstream coupling to legacy flat keys, and publish a final verification summary before closing the ingestion-side migration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Integration tests cover operation-key schema parsing, JSONB persistence, absolute-path lookup parity, and at least one representative end-to-end FastAPI or Next.js regression.
- [ ] #2 Verification runs typecheck before lint and targeted test execution in the affected Python packages.
- [ ] #3 Any residual downstream coupling to legacy flat feature keys is documented in task notes and linked follow-up work rather than silently folded into this task.
<!-- AC:END -->
