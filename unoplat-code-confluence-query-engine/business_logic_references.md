# Business Logic References

## Domain Summary
The query/analysis engine coordinates AI agents to inspect repositories, capture events and outputs, and persist workflow results. It models provider configuration (including OAuth connectivity), tool/MCP setup, repository metadata, structured analysis outputs (business logic domains, interfaces, managed markdown artifacts, engineering workflows), and usage/cost statistics to support LLM-driven processing across codebases.

## Core Modules and Responsibilities

| Area | Path | Responsibility |
| --- | --- | --- |
| API endpoints | `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py` | CRUD endpoints for AI model provider configuration. |
| API endpoints | `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py` | Manage agent rules scoped to a codebase. |
| API endpoints | `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py` | Feature flag management endpoints. |
| API endpoints | `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py` | Tool/MCP server configuration endpoints. |
| Persistence | `src/unoplat_code_confluence_query_engine/db/postgres/ai_model_config.py` | Postgres access for AI model configuration records. |
| Persistence | `src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_business_logic_repository.py` | Repository for core business-logic queries and persistence. |
| Models/config | `src/unoplat_code_confluence_query_engine/models/config/ai_model_config.py` | Pydantic schema for AI model provider settings. |
| Models/config | `src/unoplat_code_confluence_query_engine/models/config/mcp_config.py` | MCP/tool server configuration schemas. |
| Models/events | `src/unoplat_code_confluence_query_engine/models/events/agent_events.py` | Agent event payload definitions. |
| Models/output | `src/unoplat_code_confluence_query_engine/models/output/agent_md_output.py` | Markdown output schema for agent responses. |
| Models/output | `src/unoplat_code_confluence_query_engine/models/output/engineering_workflow_output.py` | Engineering workflow output schema. |
| Models/repository | `src/unoplat_code_confluence_query_engine/models/repository/repository_ruleset_metadata.py` | Repository ruleset metadata model. |
| Models/runtime | `src/unoplat_code_confluence_query_engine/models/runtime/agent_dependencies.py` | Runtime dependency definitions for agents. |
| Models/statistics | `src/unoplat_code_confluence_query_engine/models/statistics/agent_usage_statistics.py` | Usage/cost statistics schemas. |
| Services/config | `src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py` | OAuth configuration and token handling for providers. |
| Services/config | `src/unoplat_code_confluence_query_engine/services/config/provider_catalog.py` | Registry of available model providers and capabilities. |
| Services/workflow | `src/unoplat_code_confluence_query_engine/services/temporal/workflow_envelopes.py` | Temporal workflow envelope/payload helpers for orchestration. |
| Tools | `src/unoplat_code_confluence_query_engine/tools/search_across_codebase.py` | Search tool for scanning repositories and aggregating results. |