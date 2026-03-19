---
id: TASK-1.3
title: >-
  Expand Next.js app-interface detection to exported const route handlers and
  TSX route files
status: To Do
assignee: []
created_date: '2026-03-07 11:32'
updated_date: '2026-03-19 09:57'
labels:
  - typescript
  - nextjs
  - app-interfaces
  - framework-detection
dependencies: []
references:
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/nextjs.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/language_processors/typescript_processor.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_framework_query_builder.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/queries/function_definition.scm
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/tests/engine/programming_language/typescript/test_nextjs_extraction.py
  - >-
    /Users/jayghiya/Documents/unoplat/onyx/web/src/app/auth/oidc/callback/route.ts
  - /Users/jayghiya/Documents/unoplat/onyx/web/src/app/auth/logout/route.ts
  - >-
    /Users/jayghiya/Documents/unoplat/onyx/web/src/app/connector/oauth/callback/[source]/route.tsx
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/logs/unoplat-code-confluence_2026-03-07_10-26-01.log
documentation:
  - 'https://nextjs.org/docs/app/building-your-application/routing/route-handlers'
  - 'https://nextjs.org/docs/app/api-reference/file-conventions/route'
parent_task_id: TASK-1
priority: high
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Close the current Next.js App Router detection gap in the TypeScript ingestion pipeline. Today we recognize supported `route.ts` handlers written as exported function declarations, but valid route handlers written as exported const async functions and handlers defined in `route.tsx` files are not consistently surfaced as app interfaces. This causes undercounting in real codebases such as Onyx web even when the routes use legitimate Next.js App Router patterns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 TypeScript Next.js app-interface detection recognizes App Router handlers written as `export const GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS = async ...` when the existing `next/server` import gate is satisfied.
- [ ] #2 The TypeScript/TSX parsing path processes `route.tsx` files so supported Next.js route handlers in TSX files can be emitted as `nextjs.http_endpoint` detections.
- [ ] #3 Existing support for `export async function GET/POST/...` route handlers in `.ts` files remains intact.
- [ ] #4 Negative cases remain guarded: non-HTTP export names or files without the required `next/server` import evidence do not produce Next.js app-interface detections.
- [ ] #5 Targeted tests cover function-declaration handlers, exported-const async handlers, TSX route handlers, and an Onyx-inspired regression sample demonstrating the previously missed forms.
- [ ] #6 Contributor-facing docs or implementation notes are updated anywhere the supported Next.js route-handler forms are described so the detection contract matches runtime behavior.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1) Extend the TypeScript query/detector contract for Next.js route handlers.
- Add support for exported variable-based async handler forms (`export const GET = async (...) => {}` and equivalent HTTP verbs) in the TypeScript `FunctionDefinition` detection path.
- Preserve the current `next/server` import gate and existing export-name regex contract so false-positive behavior does not broaden unexpectedly.

2) Add TSX route-file support in the TypeScript language processor.
- Update the TypeScript processor/source-context path so `route.tsx` files are parsed for framework detection instead of being skipped.
- Keep declaration-file exclusions and avoid broad unrelated TSX semantic changes beyond what is needed for route-handler detection.

3) Add focused regression coverage.
- Positive tests for `export async function GET(...)` in `.ts`.
- Positive tests for `export const GET = async (...) => ...` in `.ts`.
- Positive tests for a supported `route.tsx` handler.
- Negative tests for missing `next/server` imports and non-HTTP export names.
- Add an Onyx-inspired sample covering currently missed route forms.

4) Align docs and validate.
- Update any Next.js detection notes/tests/examples so supported handler forms are explicit.
- Run targeted TypeScript framework-detection checks and confirm the missed Onyx-style handlers are now emitted as `nextjs.http_endpoint`.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Observed gap from 2026-03-07 Onyx investigation: ingestion stored 8 `nextjs.http_endpoint` rows for `/opt/unoplat/repositories/onyx/web/src/app/api/[...path]/route.ts` and `/opt/unoplat/repositories/onyx/web/src/app/api/chat/mcp/oauth/callback/route.ts`, but route files using `export const GET/POST = async ...` logged `count=0` in `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/logs/unoplat-code-confluence_2026-03-07_10-26-01.log`.

Current root causes identified: `function_definition.scm` only matches exported `function_declaration` nodes, and `typescript_processor.py` currently supports only `.ts` files while explicitly deferring `.tsx` support.
<!-- SECTION:NOTES:END -->
