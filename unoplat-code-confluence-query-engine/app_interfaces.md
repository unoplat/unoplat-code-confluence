# App Interfaces

Format: `path: L<line>: <match_text>` where path is codebase-relative.

## Inbound Constructs

### http_endpoint (fastapi)

- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L260: @router.get("/model-config", response_model=AiModelConfigOut)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L300: @router.put("/model-config", response_model=AiModelConfigOut)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L364: @router.delete("/model-config")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L399: @router.get("/providers", response_model=Dict[str, ProviderSchemaPublic])
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L419: @router.get("/providers/{provider_key}", response_model=ProviderSchema)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L453: @router.post( "/model-config/codex-openai/oauth/authorize", response_model=CodexOAuthAuthorizeResponse, )
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L488: @router.get( "/model-config/codex-openai/oauth/flows/{flow_id}", response_model=CodexOAuthFlowStatusResponse, )
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L555: @router.get("/model-config/codex-openai/oauth/callback", response_class=HTMLResponse)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L573: @callback_router.get("/auth/callback", response_class=HTMLResponse)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L591: @router.get( "/model-config/codex-openai/oauth/status", response_model=CodexOAuthConnectionStatusResponse, )
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py`: L610: @router.delete( "/model-config/codex-openai/oauth", response_model=CodexOAuthDeleteResponse, )
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/app_feedback.py`: L35: @router.post("", response_model=AppFeedbackResponse)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L255: @router.get("/codebase-agent-rules")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L363: @router.post("/repository-agent-run/cancel")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L497: @router.get("/repository-agent-snapshot")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L562: @router.post("/repository-agent-md-pr")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L968: @router.get("/repository-agent-md-pr")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py`: L124: @router.delete("/flags/{flag_name}")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py`: L21: @router.get("/flags", response_model=List[Dict[str, Any]])
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py`: L47: @router.get("/flags/{flag_name}", response_model=Dict[str, Any])
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py`: L87: @router.put("/flags/{flag_name}", response_model=Dict[str, Any])
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py`: L101: @router.put("/{provider}", response_model=ToolConfigResponse)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py`: L129: @router.get("/{provider}", response_model=ToolConfigResponse)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py`: L149: @router.get("", response_model=ToolConfigListResponse)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py`: L177: @router.delete("/{provider}", response_model=ToolConfigDeleteResponse)

## Outbound Constructs

### mcp_client (fastmcp)

- `src/unoplat_code_confluence_query_engine/services/mcp/mcp_server_manager.py`: L125: FastMCPToolset(mcp_config, id=id_value)
- `src/unoplat_code_confluence_query_engine/services/mcp/mcp_server_manager.py`: L188: FastMCPToolset(mcp_config, id=id_value)

## Internal Constructs

No internal constructs detected.
