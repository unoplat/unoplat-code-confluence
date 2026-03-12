---
id: TASK-6
title: >-
  Add DuckDuckGo fallback for Temporal agents and remove Exa-only launch
  constraint
status: Done
assignee: []
created_date: '2026-03-03 05:52'
updated_date: '2026-03-10 09:31'
labels:
  - query-engine
  - agents
  - web-search
  - fallback
  - frontend
dependencies: []
priority: high
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement ordered external-search fallback for Temporal agents that require official documentation lookup: (1) Exa MCP when configured, (2) provider-native built-in WebSearchTool when supported, (3) DuckDuckGo common tool fallback when Exa and native web search are unavailable. Remove the current backend/frontend Exa-only launch constraint so Agent MD operations can run for providers like Bedrock without Exa. Keep agent scope to development_workflow_guide, dependency_guide, and call_expression_validator; leave business_domain_guide and agents_md_updater unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Search mode resolves in strict order: exa (if configured) > builtin_web_search (if provider supported) > duckduckgo.
- [x] #2 For provider bedrock with Exa not configured, temporal agents initialize and use DuckDuckGo fallback for designated search-dependent agents.
- [x] #3 development_workflow_guide, dependency_guide, and call_expression_validator receive DuckDuckGo fallback when selected; business_domain_guide and agents_md_updater do not.
- [x] #4 Backend start endpoint no longer returns Exa-required 503 when provider lacks built-in web search support and Exa is not configured.
- [x] #5 Frontend no longer forces Exa setup action from old Exa-only error string matching during Agent MD launch.
- [x] #6 Dependency configuration includes DuckDuckGo support and runtime can import/use pydantic_ai.common_tools.duckduckgo.duckduckgo_search_tool.
- [ ] #7 Tests cover fallback resolution, prompt instruction branching, and launch behavior for non-native providers without Exa.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementation plan (approved by user request to start implementation):
1. Update search-mode constants/instructions in src/unoplat_code_confluence_query_engine/agents/code_confluence_agents.py to add SEARCH_MODE_DUCKDUCKGO, add DuckDuckGo-specific official-doc instructions/workflow steps, and make no-search engineering citation guidance conservative/non-throwing.
2. Update Temporal agent wiring in src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py:
   - import duckduckgo_search_tool from pydantic_ai.common_tools.duckduckgo
   - add helper to build DuckDuckGo common tool list for selected agents
   - resolve mode ordering exa > builtin_web_search > duckduckgo > none
   - wire fallback only for development_workflow_guide, dependency_guide, call_expression_validator; keep business_domain_guide and agents_md_updater unchanged
3. Remove Exa-only backend launch gate in src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py so launch is not blocked when Exa is absent for non-native providers.
4. Remove Exa-string-matching frontend branch in unoplat-code-confluence-frontend/src/components/custom/IngestedRepositoriesDataTable.tsx so launch failures are surfaced directly without forcing Exa setup.
5. Update query-engine dependencies to include DuckDuckGo support (pydantic-ai-slim[duckduckgo]) and refresh uv.lock.
6. Add tests for search mode resolution and prompt instruction branching in query-engine tests; run typecheck then lint and targeted tests.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented DuckDuckGo fallback search mode and prompt branching across code_confluence_agents.py and temporal_agents.py.

Search mode resolution now follows exa -> builtin_web_search -> duckduckgo; DuckDuckGo tool wiring is limited to development_workflow_guide, dependency_guide, and call_expression_validator.

Removed Exa-only preflight gate from start_repository_agent_run so launch no longer hard-fails solely due missing Exa.

Removed frontend Exa-specific error-toast branch in IngestedRepositoriesDataTable; launch failures now surface backend message directly.

Updated query-engine dependency to pydantic-ai-slim[bedrock,duckduckgo,retries] and ran uv sync; verified duckduckgo_search_tool import resolves at runtime.

Per user instruction, did not add tests and left manual verification to user.
<!-- SECTION:NOTES:END -->
