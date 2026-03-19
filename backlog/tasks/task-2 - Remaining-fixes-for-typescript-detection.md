---
id: TASK-2
title: Remaining fixes for typescript detection
status: To Do
assignee: []
created_date: '2026-02-28 06:59'
updated_date: '2026-03-19 09:57'
labels: []
dependencies: []
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
11. You missed updating TypeScript processor v1 contract comments/tests.
- Gap: current file explicitly says framework/import extraction is deferred v1 in unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/language_processors/typescript_processor.py.
- Fix: update docstring/tests in tests/parser/language_processors/test_typescript_processor.py that currently assert imports are intentionally omitted.
12. You missed test impact from hardcoded framework counts.
- Gap: several ingestion tests hardcode 4/7/11 counts in tests/integration/test_framework_definitions_ingestion.py.
- Fix: if any test path starts loading all language dirs (not just python/), those assertions must become dynamic or updated.
13. README/docs update is missing from execution steps.
- Gap: framework-definitions/README.md still says TypeScript is “future framework definitions.”
- Fix: update unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/README.md once typescript/nextjs.json exists.
14. Query-engine retrieval verification is missing as a test step.
- Gap: plan validates ingestion/detection but not downstream retrieval behavior.
- Fix: add at least one assertion path for db_get_all_framework_features_for_codebase(..., programming_language="typescript") in query-engine tests, especially if you keep non-standard feature key.
15. Minor but important: route.ts file-convention gating is not represented.
- Gap: your detector may match any exported GET/POST in any .ts importing next/server.
- Fix: either explicitly accept this heuristic in task notes, or extend interface to pass file path and gate by filename in a follow-up.
<!-- SECTION:DESCRIPTION:END -->
