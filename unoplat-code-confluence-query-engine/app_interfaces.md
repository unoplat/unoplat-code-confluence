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
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L130: @router.get("/codebase-agent-rules")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L268: @router.post("/repository-agent-run/cancel")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L402: @router.get("/repository-agent-snapshot")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L500: @router.post("/repository-agent-md-pr")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py`: L560: @router.get("/repository-agent-md-pr")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py`: L124: @router.delete("/flags/{flag_name}")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py`: L21: @router.get("/flags", response_model=List[Dict[str, Any]])
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py`: L47: @router.get("/flags/{flag_name}", response_model=Dict[str, Any])
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py`: L87: @router.put("/flags/{flag_name}", response_model=Dict[str, Any])
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/health.py`: L13: @router.get("/health")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/health.py`: L26: @router.get("/ready")
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py`: L101: @router.put("/{provider}", response_model=ToolConfigResponse)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py`: L129: @router.get("/{provider}", response_model=ToolConfigResponse)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py`: L149: @router.get("", response_model=ToolConfigListResponse)
- `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py`: L177: @router.delete("/{provider}", response_model=ToolConfigDeleteResponse)

## Outbound Constructs

### db_sql (sqlalchemy)

- `src/unoplat_code_confluence_query_engine/services/flags/flag_service.py`: L132: session.delete(flag)
- `src/unoplat_code_confluence_query_engine/services/flags/flag_service.py`: L95: session.add(flag)

### http_client (ghapi)

- `src/unoplat_code_confluence_query_engine/services/feedback/app_feedback_service.py`: L101: api.issues.create( # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType,reportAttributeAccessIssue] title=title, body=body, labels=labels, )
- `src/unoplat_code_confluence_query_engine/services/feedback/app_feedback_service.py`: L91: GhApi( owner=_TARGET_OWNER, repo=_TARGET_REPO, token=token, gh_host=_GITHUB_HOST, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L103: new_commit = api.git.create_commit( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, message=f"Update codebase artifacts from run {repository_workflow_run_id}", tree=new_tree_sha, parents=[head_sha], )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L113: api.git.create_ref( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue] owner=owner_name, repo=repo_name, ref=f"refs/heads/{branch_name}", sha=new_commit_sha, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L122: api.git.update_ref( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue] owner=owner_name, repo=repo_name, ref=f"heads/{branch_name}", sha=new_commit_sha, force=True, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L139: created_pr = api.pulls.create( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, title=pr_title, head=branch_name, base=default_branch, body="\n".join(pr_body_lines), )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L29: repo_info = api.repos.get(owner=owner_name, repo=repo_name) # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L34: base_commit = api.repos.get_commit( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, ref=default_branch, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L54: pulls = api.pulls.list( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, state="open", head=f"{owner_name}:{branch_name}", base=default_branch, per_page=1, page=1, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L89: new_tree = api.git.create_tree( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, base_tree=base_tree_sha, tree=tree_entries, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_service.py`: L389: GhApi( owner=owner_name, repo=repo_name, token=repository_pat, gh_host=github_host, )
- `src/unoplat_code_confluence_query_engine/services/github/git_ref_resolver.py`: L28: repo_info = api.repos.get(owner=owner, repo=repo) # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
- `src/unoplat_code_confluence_query_engine/services/github/git_ref_resolver.py`: L33: ref_info = api.git.get_ref( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner, repo=repo, ref=f"heads/{default_branch}", )
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/git_ref_resolution_activity.py`: L101: GhApi( owner=owner_name, repo=repo_name, token=repository_pat, gh_host=github_host, )
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/repository_workflow_run/git_ref_resolution_activity.py`: L101: GhApi( owner=owner_name, repo=repo_name, token=repository_pat, gh_host=github_host, )

### http_client (httpx)

- `src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py`: L284: client.post( f"{self._settings.codex_openai_issuer}/oauth/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={ "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri, "client_id": self._settings.codex_openai_client_id, "code_verifier": verifier, }, )
- `src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py`: L302: client.post( f"{self._settings.codex_openai_issuer}/oauth/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={ "grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": self._settings.codex_openai_client_id, }, )
- `src/unoplat_code_confluence_query_engine/utils/retry_http_client.py`: L122: AsyncClient( transport=transport, timeout=settings.retry_timeout, )

### llm_inference (pydantic_ai)

- `src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/agents/business_domain.py`: L50: Agent( context.model, name="business_domain_guide", instructions=build_business_domain_instructions(), deps_type=AgentDependencies, tools=tuple(function_tools), capabilities=[console_capability], output_type=str, output_retries=3, model_settings=context.model_settings, event_stream_handler=event_stream_handler, )
- `src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/agents/call_expression_validator.py`: L88: Agent( context.model, name="call_expression_validator", instructions=build_call_expression_validator_instructions(), deps_type=AgentDependencies, tools=tuple(function_tools), toolsets=tuple(toolsets), capabilities=capabilities, output_type=CallExpressionValidationAgentOutput, output_retries=2, model_settings=context.model_settings, event_stream_handler=event_stream_handler, )
- `src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/agents/dependency_guide.py`: L83: Agent( context.model, name="dependency_guide", instructions=build_dependency_guide_instructions(), deps_type=AgentDependencies, tools=tuple(function_tools), toolsets=tuple(toolsets), capabilities=capabilities, output_type=DependencyGuideEntry, output_retries=2, model_settings=context.model_settings, event_stream_handler=event_stream_handler, )
- `src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/agents/development_workflow.py`: L106: Agent( context.model, name="development_workflow_guide", instructions=build_development_workflow_instructions(), deps_type=AgentDependencies, toolsets=tuple(toolsets), capabilities=capabilities, output_type=EngineeringWorkflowAgentOutput, output_retries=2, model_settings=context.model_settings, event_stream_handler=event_stream_handler, )
- `src/unoplat_code_confluence_query_engine/services/temporal/agent_assembly/assembler.py`: L94: TemporalAgent( build_result.agent, activity_config=activity_config.activity_config, model_activity_config=activity_config.model_activity_config, toolset_activity_config=activity_config.toolset_activity_config, tool_activity_config=activity_config.tool_activity_config, )
- `tests/services/test_development_workflow_runtime.py`: L170: Agent( model, deps_type=AgentDependencies, output_type=EngineeringWorkflowAgentOutput, output_retries=1, )
- `tests/services/test_development_workflow_runtime.py`: L252: Agent( model, deps_type=AgentDependencies, output_type=PromptedOutput(EngineeringWorkflowAgentOutput), output_retries=1, )

### mcp_client (fastmcp)

- `src/unoplat_code_confluence_query_engine/services/mcp/mcp_server_manager.py`: L125: FastMCPToolset(mcp_config, id=id_value)
- `src/unoplat_code_confluence_query_engine/services/mcp/mcp_server_manager.py`: L188: FastMCPToolset(mcp_config, id=id_value)

## Bidirectional Constructs

No bidirectional constructs detected.

## Internal Constructs

No internal constructs detected.
