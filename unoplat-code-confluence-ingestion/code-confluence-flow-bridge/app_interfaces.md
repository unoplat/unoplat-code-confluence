# App Interfaces

Format: `path: L<line>: <match_text>` where path is codebase-relative.

## Inbound Constructs

### http_endpoint (fastapi)

- `src/code_confluence_flow_bridge/github_app/router.py`: L144: @router.get( "/app-manifest/callback", response_model=ManifestConversionResponse, status_code=status.HTTP_200_OK, )
- `src/code_confluence_flow_bridge/github_app/router.py`: L245: @router.post( "/webhook", status_code=status.HTTP_202_ACCEPTED, )
- `src/code_confluence_flow_bridge/github_app/router.py`: L55: @router.post( "/app-manifest", response_model=ManifestGenerationResponse, status_code=status.HTTP_201_CREATED, )
- `src/code_confluence_flow_bridge/main.py`: L419: @app.post("/start-ingestion", status_code=201)
- `src/code_confluence_flow_bridge/routers/credentials/router.py`: L23: @router.post("/ingest-token", status_code=201)
- `src/code_confluence_flow_bridge/routers/credentials/router.py`: L55: @router.put("/update-token", status_code=200)
- `src/code_confluence_flow_bridge/routers/credentials/router.py`: L87: @router.delete("/delete-token", status_code=200)
- `src/code_confluence_flow_bridge/routers/flags/router.py`: L14: @router.get("/flags/{flag_name}", status_code=200)
- `src/code_confluence_flow_bridge/routers/flags/router.py`: L34: @router.get("/flags", status_code=200)
- `src/code_confluence_flow_bridge/routers/flags/router.py`: L48: @router.put("/flags/{flag_name}", status_code=200)
- `src/code_confluence_flow_bridge/routers/github_issues/router.py`: L203: @router.post("/feedback", response_model=IssueTracking)
- `src/code_confluence_flow_bridge/routers/github_issues/router.py`: L49: @router.post("/issues", response_model=IssueTracking)
- `src/code_confluence_flow_bridge/routers/health/router.py`: L13: @router.get("/health")
- `src/code_confluence_flow_bridge/routers/health/router.py`: L26: @router.get("/ready")
- `src/code_confluence_flow_bridge/routers/operations/router.py`: L32: @router.get( "/parent-workflow-jobs", response_model=ParentWorkflowJobListResponse, description="Get all parent workflow jobs data without pagination", )
- `src/code_confluence_flow_bridge/routers/operations/router.py`: L84: @router.get( "/get/ingestedRepositories", response_model=IngestedRepositoriesListResponse, description="Get all ingested repositories without pagination", )
- `src/code_confluence_flow_bridge/routers/providers/router.py`: L22: @router.get("/repository-providers", response_model=RepositoryProvidersResponse)
- `src/code_confluence_flow_bridge/routers/providers/router.py`: L36: @router.get("/repos", response_model=PaginatedResponse)
- `src/code_confluence_flow_bridge/routers/providers/router.py`: L63: @router.get("/user-details", status_code=200)
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L160: @router.get( "/repository-data", response_model=GitHubRepoResponseConfiguration, )
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L218: @router.get( "/codebase-metadata", response_model=CodebaseMetadataListResponse, )
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L282: @router.delete("/delete-repository", status_code=200)
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L372: @router.post("/repositories", response_model=RepositoryAddResponse, status_code=201)
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L467: @router.post( "/refresh-repository", response_model=RefreshRepositoryResponse, status_code=201 )
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L85: @router.get( "/repository-status", response_model=GithubRepoStatus, )

### scheduler_trigger (temporalio)

- `src/code_confluence_flow_bridge/processor/agent_md_update_activity.py`: L25: @activity.defn(name="trigger-agent-md-update")
- `src/code_confluence_flow_bridge/processor/codebase_child_workflow.py`: L35: @workflow.defn(name="child-codebase-workflow")
- `src/code_confluence_flow_bridge/processor/db/postgres/child_workflow_db_activity.py`: L29: @activity.defn(name="update-codebase-workflow-status")
- `src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py`: L29: @activity.defn(name="update-repository-workflow-status")
- `src/code_confluence_flow_bridge/processor/generic_codebase_processing_activity.py`: L38: @activity.defn
- `src/code_confluence_flow_bridge/processor/git_activity/confluence_git_activity.py`: L26: @activity.defn
- `src/code_confluence_flow_bridge/processor/git_activity/confluence_git_graph.py`: L36: @activity.defn
- `src/code_confluence_flow_bridge/processor/package_metadata_activity/package_manager_metadata_activity.py`: L24: @activity.defn
- `src/code_confluence_flow_bridge/processor/package_metadata_activity/package_manager_metadata_ingestion.py`: L29: @activity.defn
- `src/code_confluence_flow_bridge/processor/repo_workflow.py`: L45: @workflow.defn(name="repo-activity-workflow")

## Outbound Constructs

### db_sql (sqlalchemy)

- `src/code_confluence_flow_bridge/github_app/service.py`: L192: session.execute( delete(GithubAppManifestRecord).where(GithubAppManifestRecord.state == state) )
- `src/code_confluence_flow_bridge/github_app/service.py`: L193: delete(GithubAppManifestRecord)
- `src/code_confluence_flow_bridge/github_app/service.py`: L195: session.add(record)
- `src/code_confluence_flow_bridge/github_app/service.py`: L214: session.delete(record)
- `src/code_confluence_flow_bridge/github_app/service.py`: L221: delete(GithubAppManifestRecord)
- `src/code_confluence_flow_bridge/github_app/service.py`: L225: session.execute(stmt)
- `src/code_confluence_flow_bridge/github_app/service.py`: L258: session.add(credential)
- `src/code_confluence_flow_bridge/github_app/service.py`: L260: session.add( Credentials( credential_key=key, token_hash=encrypted_value, created_at=current_time, updated_at=current_time, ) )
- `src/code_confluence_flow_bridge/processor/db/postgres/child_workflow_db_activity.py`: L126: session.add(workflow_run)
- `src/code_confluence_flow_bridge/processor/db/postgres/child_workflow_db_activity.py`: L141: session.add(workflow_run)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L106: insert(UnoplatCodeConfluenceGitRepository)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L111: self.session.execute(stmt)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L136: insert(UnoplatCodeConfluenceCodebase)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L141: self.session.execute(stmt)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L156: insert(UnoplatCodeConfluencePackageManagerMetadata).values( codebase_qualified_name=codebase_qualified_name, **payload, )
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L164: self.session.execute(stmt)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L181: insert(UnoplatCodeConfluenceFile)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L186: self.session.execute(stmt)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L199: insert(UnoplatCodeConfluenceCodebaseFramework)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L207: self.session.execute(stmt)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L229: insert(UnoplatCodeConfluenceFileFrameworkFeature)
- `src/code_confluence_flow_bridge/processor/db/postgres/code_confluence_relational_ingestion.py`: L241: self.session.execute(stmt)
- `src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py`: L298: session.execute(delete(FeatureAbsolutePath))
- `src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py`: L299: session.execute(delete(FrameworkFeature))
- `src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py`: L300: session.execute(delete(Framework))
- `src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py`: L304: session.add_all(frameworks)
- `src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py`: L305: session.add_all(features)
- `src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py`: L306: session.add_all(absolute_paths)
- `src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py`: L122: session.add(workflow_run)
- `src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py`: L157: session.add(workflow_run)
- `src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py`: L192: session.add(repository)
- `src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py`: L91: session.add(config)
- `src/code_confluence_flow_bridge/processor/db/postgres/parent_workflow_db_activity.py`: L96: session.add(existing_config)
- `src/code_confluence_flow_bridge/routers/credentials/service.py`: L119: session.add(credential)
- `src/code_confluence_flow_bridge/routers/credentials/service.py`: L139: session.delete(credential)
- `src/code_confluence_flow_bridge/routers/credentials/service.py`: L57: session.add(token_flag)
- `src/code_confluence_flow_bridge/routers/credentials/service.py`: L80: session.add( Credentials( namespace=namespace, provider_key=provider_key, secret_kind=secret_kind, token_hash=encrypt_token(token), metadata_json=build_credential_metadata(url), created_at=current_time, updated_at=current_time, ) )
- `src/code_confluence_flow_bridge/routers/flags/router.py`: L62: session.add(flag)
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L324: session.delete(db_obj)
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L327: session.delete(relational_repo)
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L425: session.add(repository)

### graphql_client (gql)

- `src/code_confluence_flow_bridge/routers/providers/service.py`: L211: GQLClient( transport=transport, fetch_schema_from_transport=False, )

### http_client (httpx)

- `src/code_confluence_flow_bridge/github_app/router.py`: L172: httpx.AsyncClient(timeout=30.0)
- `src/code_confluence_flow_bridge/github_app/router.py`: L174: client.post( conversion_url, headers={ "Accept": "application/json", "Content-Type": "application/json", "User-Agent": "unoplat-code-confluence", }, )
- `src/code_confluence_flow_bridge/routers/providers/service.py`: L271: httpx.AsyncClient()
- `src/code_confluence_flow_bridge/routers/providers/service.py`: L272: client.get(f"{api_base_url}/user", headers=headers)
- `src/code_confluence_flow_bridge/routers/providers/service.py`: L283: client.get( f"{api_base_url}/user/emails", headers=headers )

### http_client (httpx2)

- `src/code_confluence_flow_bridge/processor/agent_md_update_activity.py`: L54: httpx2.get( url, params=params, headers={"Accept": "application/json"}, timeout=settings.query_engine_request_timeout_seconds, )

### task_queue_enqueue (temporalio)

- `src/code_confluence_flow_bridge/processor/codebase_child_workflow.py`: L123: workflow.execute_activity( activity=GenericCodebaseProcessingActivity.process_codebase_generic, args=[codebase_processing_envelope], start_to_close_timeout=timedelta(weeks=1), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/processor/codebase_child_workflow.py`: L81: workflow.execute_activity( activity=PackageMetadataActivity.get_package_metadata, args=[package_metadata_envelope], start_to_close_timeout=timedelta(minutes=10), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/processor/codebase_child_workflow.py`: L97: workflow.execute_activity( activity=PackageManagerMetadataIngestion.insert_package_manager_metadata, args=[package_manager_metadata_envelope], start_to_close_timeout=timedelta(minutes=10), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/processor/parent_workflow_interceptor.py`: L122: workflow.execute_activity( activity=ParentWorkflowDbActivity.update_repository_workflow_status, args=[running_env], start_to_close_timeout=timedelta(minutes=1), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/processor/parent_workflow_interceptor.py`: L199: workflow.execute_activity( activity=ParentWorkflowDbActivity.update_repository_workflow_status, args=[final_env], start_to_close_timeout=timedelta(minutes=1), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/processor/parent_workflow_interceptor.py`: L263: workflow.execute_activity( activity=ChildWorkflowDbActivity.update_codebase_workflow_status, args=[running_child_env], start_to_close_timeout=timedelta(minutes=1), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/processor/parent_workflow_interceptor.py`: L345: workflow.execute_activity( activity=ChildWorkflowDbActivity.update_codebase_workflow_status, args=[final_child_env], start_to_close_timeout=timedelta(minutes=1), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/processor/parent_workflow_interceptor.py`: L368: workflow.execute_activity( activity=ParentWorkflowDbActivity.update_repository_workflow_status, args=[parent_failed_env], start_to_close_timeout=timedelta(minutes=1), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/processor/repo_workflow.py`: L142: workflow.start_child_workflow( CodebaseChildWorkflow.run, args=[child_workflow_envelope], id=child_workflow_id, # use default TERMINATE policy (omit or set explicitly) parent_close_policy=ParentClosePolicy.TERMINATE, )
- `src/code_confluence_flow_bridge/processor/repo_workflow.py`: L188: workflow.execute_activity( activity=AgentMdUpdateActivity.trigger_agent_md_update, args=[agent_md_update_envelope], start_to_close_timeout=timedelta(seconds=30), retry_policy=RetryPolicy( maximum_attempts=8, initial_interval=timedelta(seconds=5), backoff_coefficient=2.0, maximum_interval=timedelta(minutes=2), ), )
- `src/code_confluence_flow_bridge/processor/repo_workflow.py`: L80: workflow.execute_activity( activity=GitActivity.process_git_activity, args=[git_activity_envelope], start_to_close_timeout=timedelta(minutes=10), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/processor/repo_workflow.py`: L96: workflow.execute_activity( activity=ConfluenceGitGraph.insert_git_repo_into_graph_db, args=[git_graph_envelope], start_to_close_timeout=timedelta(minutes=10), retry_policy=ActivityRetriesConfig.DEFAULT, )
- `src/code_confluence_flow_bridge/utility/workflow_helpers.py`: L58: temporal_client.start_workflow( RepoWorkflow.run, arg=envelope, id=workflow_id, task_queue="unoplat-code-confluence-repository-context-ingestion", )

## Bidirectional Constructs

No bidirectional constructs detected.

## Internal Constructs

No internal constructs detected.
