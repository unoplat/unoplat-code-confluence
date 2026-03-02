---
id: TASK-3
title: Add framework definitions and architectural enums for Onyx-class AI codebases
status: In Progress
assignee: []
created_date: '2026-03-02 06:36'
updated_date: '2026-03-02 11:52'
labels:
  - framework-definitions
  - schema
  - agent-md
  - ai-architecture
  - typescript
  - python
dependencies: []
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context

The Onyx codebase (at `/Users/jayghiya/Documents/unoplat/onyx`) is a sophisticated AI search/RAG platform analyzed to identify major frameworks not yet covered by the framework detection system. The current system only covers 5 frameworks (pydantic, sqlalchemy, sqlmodel, fastapi, nextjs) but Onyx uses many more architecturally significant ones.

Additionally, `agent_md_output.py` is missing critical enum values for AI-native applications — most notably there is no `LLM_INFERENCE` outbound kind, and no `RAG_PIPELINE` or `AI_AGENT` backend architectural pattern.

## Onyx Stack Summary

- **Backend**: FastAPI + SQLAlchemy + Celery + LiteLLM + Sentence-Transformers + Vespa + FastMCP (MCP server)
- **Frontend**: Next.js 16 + React 19 + Zustand + SWR + Tailwind CSS
- **Widget**: Vite + Lit (Web Components)

---

## Part 1: New Framework Definition JSON Files

All files must follow the schema at:
`unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json`

### Python Frameworks (3 new files)

#### `framework-definitions/python/celery.json`
- **Feature `task_definition`** — `AnnotationLike`, `function`, `startpoint: true` (→ SCHEDULE inbound)
  - absolute_paths: `["celery.app.base.Celery.task", "celery.shared_task", "celery.app.task.Task"]`
  - annotation_name_regex: `"^(task|shared_task)$"`
  - Description: Celery task-decorated functions — entry points triggered by workers/beat
- **Feature `periodic_task_schedule`** — `CallExpression`, `function`
  - absolute_paths: `["celery.schedules.crontab", "celery.schedules.schedule", "celery.schedules.solar"]`
  - Description: Celery Beat periodic schedule expressions

#### `framework-definitions/python/litellm.json`
- **Feature `llm_completion`** — `CallExpression`, `function`
  - absolute_paths: `["litellm.completion", "litellm.main.completion", "litellm.acompletion", "litellm.main.acompletion"]`
  - Description: Sync/async LLM text completion — maps to LLM_INFERENCE outbound kind
- **Feature `llm_embedding`** — `CallExpression`, `function`
  - absolute_paths: `["litellm.embedding", "litellm.main.embedding", "litellm.aembedding", "litellm.main.aembedding"]`
  - Description: LLM embedding generation via unified API

#### `framework-definitions/python/fastmcp.json`
- **Feature `mcp_tool`** — `AnnotationLike`, `function`, `startpoint: true` (→ MCP_SERVER inbound)
  - absolute_paths: `["fastmcp.FastMCP.tool", "mcp.server.fastmcp.FastMCP.tool"]`
  - annotation_name_regex: `"^tool$"`
  - Description: MCP tool exposed via Model Context Protocol server
- **Feature `mcp_resource`** — `AnnotationLike`, `function`, `startpoint: true`
  - absolute_paths: `["fastmcp.FastMCP.resource", "mcp.server.fastmcp.FastMCP.resource"]`
  - annotation_name_regex: `"^resource$"`
  - Description: MCP resource exposed via Model Context Protocol server

### TypeScript Frameworks (4 new files)

#### `framework-definitions/typescript/react.json`
- **Feature `context_provider`** — `FunctionDefinition`, `function`
  - absolute_paths: `["react.createContext", "react.useContext"]`
- **Feature `state_hook`** — `CallExpression`, `function`
  - absolute_paths: `["react.useState", "react.useReducer"]`
- **Feature `effect_hook`** — `CallExpression`, `function`
  - absolute_paths: `["react.useEffect", "react.useLayoutEffect"]`
- **Feature `memo_hook`** — `CallExpression`, `function`
  - absolute_paths: `["react.useMemo", "react.useCallback", "react.memo"]`

#### `framework-definitions/typescript/zustand.json`
- **Feature `store_definition`** — `CallExpression`, `function`
  - absolute_paths: `["zustand.create", "zustand/vanilla.create", "zustand.createStore"]`
  - Description: Zustand store creation — global client-side state container
- **Feature `immer_store`** — `CallExpression`, `function`
  - absolute_paths: `["zustand/middleware/immer.immer"]`
  - Description: Zustand store with Immer middleware

#### `framework-definitions/typescript/swr.json`
- **Feature `data_fetch`** — `CallExpression`, `function`
  - absolute_paths: `["swr.default", "swr.useSWR"]`
  - Description: SWR data fetching hook with stale-while-revalidate caching
- **Feature `mutation`** — `CallExpression`, `function`
  - absolute_paths: `["swr/mutation.default", "swr/mutation.useSWRMutation"]`
  - Description: SWR mutation hook for data write operations

#### `framework-definitions/typescript/litellm.json`
- **Feature `web_component`** — `Inheritance`, `class`
  - absolute_paths: `["lit.LitElement", "lit-element.LitElement"]`
  - Description: Lit Web Component base class — custom HTML element
- **Feature `reactive_property`** — `AnnotationLike`, `function`
  - absolute_paths: `["lit.property", "lit-element.property", "lit.state", "lit-element.state"]`
  - annotation_name_regex: `"^(property|state)$"`
  - Description: Lit reactive property/state decorators

---

## Part 2: Enum Additions to agent_md_output.py

**File**: `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py`

### OutboundKind — Add `LLM_INFERENCE` (CRITICAL GAP)
```python
LLM_INFERENCE = "llm_inference"
# LLM API call: OpenAI/Anthropic/Google/Cohere/local via LiteLLM or direct SDK
```
Place after `TELEMETRY`, before `Other`.

### InboundKind — Add `MCP_SERVER`
```python
MCP_SERVER = "mcp_server"
# Model Context Protocol server: JSON-RPC 2.0 over HTTP/SSE
# Distinct from plain HTTP — protocol defines tools, resources, prompts
```
Place after `EMAIL_INBOUND`, before `Other`.

### BackendArchitecturalType — Add `RAG_PIPELINE` and `AI_AGENT`
```python
RAG_PIPELINE = "rag_pipeline"
# Retrieval-Augmented Generation: vector search → context assembly → LLM synthesis

AI_AGENT = "ai_agent"
# Agent orchestration: LLM-driven reasoning loops with tool calling (ReAct, Plan-and-Execute)
```

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `framework-definitions/python/celery.json` | CREATE |
| `framework-definitions/python/litellm.json` | CREATE |
| `framework-definitions/python/fastmcp.json` | CREATE |
| `framework-definitions/typescript/react.json` | CREATE |
| `framework-definitions/typescript/zustand.json` | CREATE |
| `framework-definitions/typescript/swr.json` | CREATE |
| `framework-definitions/typescript/litellm.json` | CREATE |
| `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py` | MODIFY |

## Verification Steps
1. Each new JSON validates against `schema.json` (required: `docs_url`, `features` with `description`, `absolute_paths`, `target_level`, `concept`)
2. Run `uv run pyright` then `uv run ruff check` on modified `agent_md_output.py`
3. Confirm `startpoint: true` features in fastmcp/celery correctly link to new InboundKind values
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 7 new framework definition JSON files created (3 Python: celery, litellm, fastmcp; 4 TypeScript: react, zustand, swr, lit)
- [ ] #2 Each JSON file validates against schema.json — all required fields present (docs_url, features with description/absolute_paths/target_level/concept)
- [ ] #3 agent_md_output.py has LLM_INFERENCE added to OutboundKind enum
- [ ] #4 agent_md_output.py has MCP_SERVER added to InboundKind enum
- [ ] #5 agent_md_output.py has RAG_PIPELINE and AI_AGENT added to BackendArchitecturalType enum
- [ ] #6 Python type check passes: uv run pyright on agent_md_output.py
- [ ] #7 Python linting passes: uv run ruff check on agent_md_output.py
- [ ] #8 Celery and FastMCP features use startpoint: true to mark entry points
- [ ] #9 LiteLLM llm_completion feature aligns with new LLM_INFERENCE OutboundKind
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
User approved execution on 2026-03-02 with scope expansion to close detector/runtime gaps.

Implementation plan:
1) Create 7 framework definition JSON files under framework-definitions/python and framework-definitions/typescript with schema-compliant fields (docs_url, features, descriptions, absolute_paths, target_level, concept, construct_query/startpoint where required).
2) Add query-engine enum values in agent_md_output.py: OutboundKind.LLM_INFERENCE, InboundKind.MCP_SERVER, BackendArchitecturalType.RAG_PIPELINE and BackendArchitecturalType.AI_AGENT.
3) Wire new feature keys into app interface mapping so celery/fastmcp/litellm features classify correctly (inbound/outbound instead of internal).
4) Expand TypeScript tree-sitter framework detection beyond FunctionDefinition to support CallExpression, Inheritance, and AnnotationLike by updating TypeScript query builder, adding concept query templates, and extending detector matching logic.
5) Add/extend tests for TypeScript detector concepts and query-engine retrieval path for db_get_all_framework_features_for_codebase(..., programming_language="typescript").
6) Update ingestion integration tests that hardcode framework counts/sets to reflect new definitions (or compute expected dynamically from loaded definitions), and update framework-definitions README TypeScript section.
7) Verify: schema validation for framework JSON files, then Python typecheck first and lint second in each affected project, then run targeted tests for changed behavior.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-03-02 progress: verified new framework-definition absolute_paths/docs_url against official documentation via framework-implementation-verifier subagents (Context7 + web sources). Applied corrections for Zustand (`zustand/vanilla.createStore`), SWR default exports (`swr.default`, `swr/mutation.default`), and Lit decorators (`lit/decorators.js.property|state`).

Implemented TypeScript detector support for `CallExpression`, `Inheritance`, and `AnnotationLike` concepts by adding query templates (`call_expression.scm`, `inheritance.scm`, `annotation_function_like.scm`) and extending query builder + detector logic for concept-specific extraction/matching.

Added framework definitions: python (`celery.json`, `litellm.json`, `fastmcp.json`) and typescript (`react.json`, `zustand.json`, `swr.json`, `litellm.json` per requester rename of lit definition).

Updated query-engine enums/mappings: added `InboundKind.MCP_SERVER`, `OutboundKind.LLM_INFERENCE`, `BackendArchitecturalType.RAG_PIPELINE`, `BackendArchitecturalType.AI_AGENT`; mapped `task_definition`, `mcp_tool`, `mcp_resource`, `llm_completion`, `llm_embedding`.

Added tests: TypeScript additional concept extraction tests, query-engine mapper unit tests, and query-engine DB retrieval test for `programming_language='typescript'`. Updated ingestion integration counts for expanded python framework set.

Validation executed: `check-jsonschema` passed; flow-bridge targeted basedpyright passed (changed files), ruff passed, targeted pytest passed (18 tests); query-engine targeted basedpyright passed (changed files), ruff passed, targeted pytest passed (3 tests).
<!-- SECTION:NOTES:END -->
