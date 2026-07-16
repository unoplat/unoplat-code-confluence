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

### scheduler_trigger (temporalio)

- `src/unoplat_code_confluence_query_engine/services/temporal/activities/app_interfaces_activity.py`: L29: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/app_interfaces_activity.py`: L67: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/app_interfaces_activity.py`: L93: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/business_logic_post_process_activity.py`: L21: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/app_interfaces_activity.py`: L124: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/app_interfaces_activity.py`: L35: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/app_interfaces_activity.py`: L75: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/app_interfaces_activity.py`: L97: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/business_logic_post_process_activity.py`: L21: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/dependency_guide_completion_activity.py`: L32: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/dependency_guide_completion_activity.py`: L77: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/dependency_guide_fetch_activity.py`: L31: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/dependency_guide_fetch_activity.py`: L57: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/engineering_workflow_completion_activity.py`: L19: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/engineering_workflow_fetch_activity.py`: L19: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/managed_block_activity.py`: L16: @activity.defn(name="bootstrap-managed-block")
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/codebase_workflow_run/managed_block_activity.py`: L37: @activity.defn(name="managed-section-has-content")
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/dependency_guide_completion_activity.py`: L19: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/dependency_guide_fetch_activity.py`: L22: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/engineering_workflow_completion_activity.py`: L19: @activity.defn
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/git_ref_resolution_activity.py`: L27: @activity.defn(name="resolve-repository-git-ref")
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/repository_workflow_run/agent_md_pr_publish_activity.py`: L25: @activity.defn(name="publish-agent-md-pr")
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/repository_workflow_run/git_ref_resolution_activity.py`: L27: @activity.defn(name="resolve-repository-git-ref")
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/activity/codebase_workflow_db_activity.py`: L20: @activity.defn(name="update-codebase-agent-workflow-status")
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/activity/repository_agent_snapshot_activity.py`: L23: @activity.defn(name="persist-agent-snapshot-begin-run")
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/activity/repository_agent_snapshot_activity.py`: L52: @activity.defn(name="persist-agent-snapshot-codebase-patch")
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/activity/repository_agent_snapshot_activity.py`: L82: @activity.defn(name="persist-agent-snapshot-complete")
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/activity/repository_workflow_db_activity.py`: L23: @activity.defn(name="update-repository-agent-workflow-status")
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/codebase_agent_workflow.py`: L46: @workflow.defn(versioning_behavior=common.VersioningBehavior.AUTO_UPGRADE)
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/repository_agent_workflow.py`: L38: @workflow.defn(versioning_behavior=common.VersioningBehavior.AUTO_UPGRADE)

## Outbound Constructs

### http_client (ghapi)

- `src/unoplat_code_confluence_query_engine/services/feedback/app_feedback_service.py`: L101: api.issues.create( # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType,reportAttributeAccessIssue] title=title, body=body, labels=labels, )
- `src/unoplat_code_confluence_query_engine/services/feedback/app_feedback_service.py`: L91: GhApi( owner=_TARGET_OWNER, repo=_TARGET_REPO, token=token, gh_host=_GITHUB_HOST, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L103: api.git.create_commit( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, message=f"Update codebase artifacts from run {repository_workflow_run_id}", tree=new_tree_sha, parents=[head_sha], )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L113: api.git.create_ref( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue] owner=owner_name, repo=repo_name, ref=f"refs/heads/{branch_name}", sha=new_commit_sha, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L122: api.git.update_ref( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue] owner=owner_name, repo=repo_name, ref=f"heads/{branch_name}", sha=new_commit_sha, force=True, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L139: api.pulls.create( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, title=pr_title, head=branch_name, base=default_branch, body="\n".join(pr_body_lines), )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L29: api.repos.get(owner=owner_name, repo=repo_name)
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L34: api.repos.get_commit( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, ref=default_branch, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L54: api.pulls.list( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, state="open", head=f"{owner_name}:{branch_name}", base=default_branch, per_page=1, page=1, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_publisher.py`: L89: api.git.create_tree( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner_name, repo=repo_name, base_tree=base_tree_sha, tree=tree_entries, )
- `src/unoplat_code_confluence_query_engine/services/github/agent_md_pr_service.py`: L389: GhApi( owner=owner_name, repo=repo_name, token=repository_pat, gh_host=github_host, )
- `src/unoplat_code_confluence_query_engine/services/github/git_ref_resolver.py`: L28: api.repos.get(owner=owner, repo=repo)
- `src/unoplat_code_confluence_query_engine/services/github/git_ref_resolver.py`: L33: api.git.get_ref( # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType] owner=owner, repo=repo, ref=f"heads/{default_branch}", )
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/git_ref_resolution_activity.py`: L101: GhApi( owner=owner_name, repo=repo_name, token=repository_pat, gh_host=github_host, )
- `src/unoplat_code_confluence_query_engine/services/temporal/activities/repository_workflow_run/git_ref_resolution_activity.py`: L101: GhApi( owner=owner_name, repo=repo_name, token=repository_pat, gh_host=github_host, )

### http_client (httpx)

- `src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py`: L223: httpx.AsyncClient(timeout=30.0)
- `src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py`: L284: client.post( f"{self._settings.codex_openai_issuer}/oauth/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={ "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri, "client_id": self._settings.codex_openai_client_id, "code_verifier": verifier, }, )
- `src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py`: L302: client.post( f"{self._settings.codex_openai_issuer}/oauth/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={ "grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": self._settings.codex_openai_client_id, }, )
- `src/unoplat_code_confluence_query_engine/services/config/codex_oauth_service.py`: L361: httpx.AsyncClient(timeout=30.0)
- `src/unoplat_code_confluence_query_engine/services/config/codex_openai_client.py`: L59: httpx.AsyncClient( transport=CodexOAuthTransport(oauth_service), timeout=timeout, )
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

### task_queue_enqueue (temporalio)

- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/inbound.py`: L153: workflow.execute_activity( RepositoryWorkflowDbActivity.update_repository_workflow_status, args=[running_envelope], start_to_close_timeout=DB_ACTIVITY_TIMEOUT, retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/inbound.py`: L179: workflow.execute_activity( RepositoryAgentSnapshotActivity.persist_agent_snapshot_begin_run, args=[begin_envelope], start_to_close_timeout=DB_ACTIVITY_TIMEOUT, retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/inbound.py`: L217: workflow.execute_activity( RepositoryWorkflowDbActivity.update_repository_workflow_status, args=[final_envelope], start_to_close_timeout=DB_ACTIVITY_TIMEOUT, retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/inbound.py`: L291: workflow.execute_activity( CodebaseWorkflowDbActivity.update_codebase_workflow_status, args=[running_envelope], start_to_close_timeout=DB_ACTIVITY_TIMEOUT, retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/inbound.py`: L336: workflow.execute_activity( CodebaseWorkflowDbActivity.update_codebase_workflow_status, args=[final_envelope], start_to_close_timeout=DB_ACTIVITY_TIMEOUT, retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/interceptors/agent_workflow/inbound.py`: L363: workflow.execute_activity( RepositoryWorkflowDbActivity.update_repository_workflow_status, args=[parent_failed_envelope], start_to_close_timeout=DB_ACTIVITY_TIMEOUT, retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflow_service.py`: L72: self._client.start_workflow( RepositoryAgentWorkflow.run, args=[ repository_qualified_name, codebase_metadata_list, trace_id, operation.value, ], id=workflow_id, task_queue=TASK_QUEUE, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/agent_snapshot_patch_runner.py`: L36: workflow.execute_activity( RepositoryAgentSnapshotActivity.persist_agent_snapshot_codebase_patch, args=[patch_envelope], start_to_close_timeout=timedelta(minutes=2), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/app_interfaces_runner.py`: L117: workflow.execute_activity( AppInterfacesActivity.emit_app_interfaces_completion, args=[ repository_qualified_name, repository_workflow_run_id, codebase_metadata.codebase_name, codebase_metadata.codebase_programming_language, ], start_to_close_timeout=timedelta(seconds=30), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/app_interfaces_runner.py`: L62: workflow.execute_activity( AppInterfacesActivity.fetch_low_confidence_call_expression_candidates, args=[ codebase_metadata.codebase_path, codebase_metadata.codebase_programming_language, ], start_to_close_timeout=timedelta(minutes=2), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/app_interfaces_runner.py`: L87: workflow.execute_activity( AppInterfacesActivity.build_app_interfaces, args=[ codebase_metadata.codebase_path, codebase_metadata.codebase_programming_language, ], start_to_close_timeout=timedelta(minutes=2), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/app_interfaces_runner.py`: L96: workflow.execute_activity( AppInterfacesActivity.write_app_interfaces, args=[ codebase_metadata.codebase_path, app_interfaces_result, ], start_to_close_timeout=timedelta(seconds=30), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/business_domain_runner.py`: L88: workflow.execute_activity( BusinessLogicPostProcessActivity.post_process_business_logic, args=[ domain_result.output, codebase_metadata.codebase_path, codebase_metadata.codebase_programming_language, ], start_to_close_timeout=timedelta(minutes=1), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/dependency_guide_runner.py`: L137: workflow.execute_activity( DependencyGuideCompletionActivity.write_dependency_overview, args=[ codebase_metadata.codebase_path, dependency_entries, codebase_metadata.codebase_package_manager, ], start_to_close_timeout=timedelta(seconds=30), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/dependency_guide_runner.py`: L155: workflow.execute_activity( DependencyGuideCompletionActivity.emit_dependency_guide_completion, args=[ repository_qualified_name, repository_workflow_run_id, codebase_metadata.codebase_name, codebase_metadata.codebase_programming_language, ], start_to_close_timeout=timedelta(seconds=30), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/dependency_guide_runner.py`: L78: workflow.execute_activity( DependencyGuideFetchActivity.fetch_dependency_guide_delta, args=[ codebase_metadata.codebase_path, codebase_metadata.codebase_programming_language, codebase_metadata.codebase_package_manager, ], start_to_close_timeout=timedelta(seconds=30), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/development_workflow_runner.py`: L154: workflow.execute_activity( EngineeringWorkflowCompletionActivity.emit_engineering_workflow_completion, args=[ repository_qualified_name, repository_workflow_run_id, codebase_metadata.codebase_name, codebase_metadata.codebase_programming_language, ], start_to_close_timeout=timedelta(seconds=30), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/development_workflow_runner.py`: L79: workflow.execute_activity( EngineeringWorkflowFetchActivity.fetch_previous_engineering_workflow, args=[ repository_qualified_name, repository_workflow_run_id, codebase_metadata.codebase_name, ], start_to_close_timeout=timedelta(seconds=30), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/managed_block_runner.py`: L30: workflow.execute_activity( ManagedBlockActivity.bootstrap, args=[ codebase_metadata.codebase_path, git_ref_info.default_branch if git_ref_info else None, git_ref_info.head_commit_sha if git_ref_info else None, ], start_to_close_timeout=timedelta(seconds=30), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/repository_codebase_children_runner.py`: L47: workflow.start_child_workflow( # type: ignore[reportUnknownMemberType] codebase_workflow_run, args=[ repository_qualified_name, codebase_dict, repository_workflow_run_id, trace_id, git_ref_info, ], id=f"{repository_qualified_name.replace('/', '-')}-{codebase_name}", parent_close_policy=ParentClosePolicy.TERMINATE, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/repository_git_ref_runner.py`: L27: workflow.execute_activity( GitRefResolutionActivity.resolve_git_ref, args=[owner_name, repo_name], start_to_close_timeout=timedelta(seconds=30), retry_policy=DB_ACTIVITY_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/repository_pr_publish_runner.py`: L46: workflow.execute_activity( AgentMdPrPublishActivity.publish_pr, args=[envelope], start_to_close_timeout=PR_PUBLISH_TIMEOUT, retry_policy=PR_PUBLISH_RETRY_POLICY, )
- `src/unoplat_code_confluence_query_engine/services/temporal/workflows/runners/repository_snapshot_completion_runner.py`: L34: workflow.execute_activity( RepositoryAgentSnapshotActivity.persist_agent_snapshot_complete, args=[complete_envelope], start_to_close_timeout=timedelta(minutes=2), retry_policy=DB_ACTIVITY_RETRY_POLICY, )

## Bidirectional Constructs

No bidirectional constructs detected.

## Internal Constructs

No internal constructs detected.
