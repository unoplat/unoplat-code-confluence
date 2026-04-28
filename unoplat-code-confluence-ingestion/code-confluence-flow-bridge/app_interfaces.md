# App Interfaces

Format: `path: L<line>: <match_text>` where path is codebase-relative.

## Inbound Constructs

### http_endpoint (fastapi)

- `src/code_confluence_flow_bridge/github_app/router.py`: L144: @router.get( "/app-manifest/callback", response_model=ManifestConversionResponse, status_code=status.HTTP_200_OK, )
- `src/code_confluence_flow_bridge/github_app/router.py`: L245: @router.post( "/webhook", status_code=status.HTTP_202_ACCEPTED, )
- `src/code_confluence_flow_bridge/github_app/router.py`: L55: @router.post( "/app-manifest", response_model=ManifestGenerationResponse, status_code=status.HTTP_201_CREATED, )
- `src/code_confluence_flow_bridge/main.py`: L410: @app.post("/start-ingestion", status_code=201)
- `src/code_confluence_flow_bridge/routers/credentials/router.py`: L23: @router.post("/ingest-token", status_code=201)
- `src/code_confluence_flow_bridge/routers/credentials/router.py`: L55: @router.put("/update-token", status_code=200)
- `src/code_confluence_flow_bridge/routers/credentials/router.py`: L87: @router.delete("/delete-token", status_code=200)
- `src/code_confluence_flow_bridge/routers/flags/router.py`: L14: @router.get("/flags/{flag_name}", status_code=200)
- `src/code_confluence_flow_bridge/routers/flags/router.py`: L34: @router.get("/flags", status_code=200)
- `src/code_confluence_flow_bridge/routers/flags/router.py`: L48: @router.put("/flags/{flag_name}", status_code=200)
- `src/code_confluence_flow_bridge/routers/github_issues/router.py`: L203: @router.post("/feedback", response_model=IssueTracking)
- `src/code_confluence_flow_bridge/routers/github_issues/router.py`: L49: @router.post("/issues", response_model=IssueTracking)
- `src/code_confluence_flow_bridge/routers/operations/router.py`: L32: @router.get( "/parent-workflow-jobs", response_model=ParentWorkflowJobListResponse, description="Get all parent workflow jobs data without pagination", )
- `src/code_confluence_flow_bridge/routers/operations/router.py`: L84: @router.get( "/get/ingestedRepositories", response_model=IngestedRepositoriesListResponse, description="Get all ingested repositories without pagination", )
- `src/code_confluence_flow_bridge/routers/providers/router.py`: L22: @router.get("/repository-providers", response_model=RepositoryProvidersResponse)
- `src/code_confluence_flow_bridge/routers/providers/router.py`: L36: @router.get("/repos", response_model=PaginatedResponse)
- `src/code_confluence_flow_bridge/routers/providers/router.py`: L63: @router.get("/user-details", status_code=200)
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L151: @router.get( "/repository-data", response_model=GitHubRepoResponseConfiguration, )
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L209: @router.get( "/codebase-metadata", response_model=CodebaseMetadataListResponse, )
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L273: @router.delete("/delete-repository", status_code=200)
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L363: @router.post( "/refresh-repository", response_model=RefreshRepositoryResponse, status_code=201 )
- `src/code_confluence_flow_bridge/routers/repository/router.py`: L76: @router.get( "/repository-status", response_model=GithubRepoStatus, )

## Outbound Constructs

No outbound constructs detected.

## Internal Constructs

No internal constructs detected.
