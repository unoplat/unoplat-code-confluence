# App Interfaces

## FastAPI Inbound HTTP Endpoints

### Ingestion & Repository Operations (`src/code_confluence_flow_bridge/main.py`)
- `POST /start-ingestion` — start ingestion workflow.
- `GET /repository-status` — retrieve repository status (response: `GithubRepoStatus`).
- `GET /repository-data` — fetch repository configuration (response: `GitHubRepoResponseConfiguration`).
- `GET /codebase-metadata` — list codebase metadata (response: `CodebaseMetadataListResponse`).
- `GET /parent-workflow-jobs` — list parent workflow jobs with cancellability metadata for operations UI gating (response: `ParentWorkflowJobListResponse`).
- `GET /get/ingestedRepositories` — list ingested repositories (response: `IngestedRepositoriesListResponse`).
- `POST /refresh-repository` — refresh repository ingestion (response: `RefreshRepositoryResponse`).
- `DELETE /delete-repository` — delete repository from tracking.

### Token & Repository Provider Management (`src/code_confluence_flow_bridge/main.py`)
- `POST /ingest-token` — store access token for ingestion.
- `PUT /update-token` — update stored access token.
- `DELETE /delete-token` — remove stored token.
- `GET /repository-providers` — list supported repository providers (response: `RepositoryProvidersResponse`).
- `GET /repos` — list repositories (response: `PaginatedResponse`).

### Feature Flags & User (`src/code_confluence_flow_bridge/main.py`)
- `GET /flags/{flag_name}` — fetch a single feature flag.
- `GET /flags` — list feature flags.
- `PUT /flags/{flag_name}` — update a feature flag.
- `GET /user-details` — retrieve user details.

### GitHub App (`src/code_confluence_flow_bridge/github_app/router.py`)
- `POST /app-manifest` — create GitHub App manifest (response: `ManifestGenerationResponse`).
- `GET /app-manifest/callback` — GitHub App manifest callback (response: `ManifestConversionResponse`).
- `POST /webhook` — GitHub App webhook receiver.

### GitHub Issues Feedback (`src/code_confluence_flow_bridge/routers/github_issues/router.py`)
- `POST /issues` — create issue feedback (response: `IssueTracking`).
- `POST /feedback` — create feedback issue (response: `IssueTracking`).
