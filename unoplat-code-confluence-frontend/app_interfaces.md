# App Interfaces

Format: `path: L<line>: <match_text>` where path is codebase-relative.

## Inbound Constructs

No inbound constructs detected.

## Outbound Constructs

### http_client (axios)

- `src/features/agent-feedback/api.ts`: L75: apiClient.post( "/code-confluence/feedback", payload, )
- `src/features/app-feedback/api.ts`: L42: queryEngineClient.post("/v1/app-feedback", payload)
- `src/lib/api.ts`: L142: apiClient.post( "/ingest-token", null, { params: queryParams, headers: { Authorization: `Bearer ${token}`, "Content-Type": undefined, }, }, )
- `src/lib/api.ts`: L219: apiClient.get("/repos", { params })
- `src/lib/api.ts`: L236: apiClient.post( "/repositories", repository, )
- `src/lib/api.ts`: L267: apiClient.put( "/update-token", null, { params: queryParams, headers: { Authorization: `Bearer ${token}`, "Content-Type": undefined, }, }, )
- `src/lib/api.ts`: L319: apiClient.delete( "/delete-token", { params: queryParams }, )
- `src/lib/api.ts`: L333: apiClient.get( `/flags/${flagName}`, )
- `src/lib/api.ts`: L362: apiClient.post( "/repository-data", config, )
- `src/lib/api.ts`: L400: apiClient.get("/repository-data", { params: { repository_name: repositoryName, repository_owner_name: ownerName, }, })
- `src/lib/api.ts`: L437: apiClient.get( "/user-details", { params: { provider_key: providerKey }, }, )
- `src/lib/api.ts`: L456: apiClient.get("/parent-workflow-jobs")
- `src/lib/api.ts`: L489: apiClient.get( "/repository-status", { params }, )
- `src/lib/api.ts`: L537: apiClient.post( "/code-confluence/issues", requestData, )
- `src/lib/api.ts`: L557: apiClient.get( "/codebase-metadata", { params }, )
- `src/lib/api.ts`: L576: apiClient.get("/get/ingestedRepositories")
- `src/lib/api.ts`: L597: apiClient.post("/refresh-repository", repository)
- `src/lib/api.ts`: L614: apiClient.delete( "/delete-repository", { data: repository }, )
- `src/lib/api.ts`: L667: queryEngineClient.get("/v1/codebase-agent-rules", { params, })
- `src/lib/api.ts`: L690: queryEngineClient.post("/v1/repository-agent-run/cancel", null, { params, })
- `src/lib/api.ts`: L705: queryEngineClient.post("/v1/repository-agent-md-pr", payload)
- `src/lib/api.ts`: L724: queryEngineClient.get("/v1/repository-agent-md-pr", { params })
- `src/lib/api.ts`: L765: queryEngineClient.get("/v1/repository-agent-snapshot", { params, })
- `src/lib/api.ts`: L862: queryEngineClient.get("/v1/providers")
- `src/lib/api.ts`: L889: queryEngineClient.get("/v1/model-config")
- `src/lib/api.ts`: L925: queryEngineClient.put( "/v1/model-config", bodyConfig, { headers }, )
- `src/lib/api.ts`: L945: queryEngineClient.delete("/v1/model-config")
- `src/lib/api.ts`: L957: queryEngineClient.post( "/v1/model-config/codex-openai/oauth/authorize", payload, )
- `src/lib/api.ts`: L972: queryEngineClient.get( `/v1/model-config/codex-openai/oauth/flows/${flowId}`, )
- `src/lib/api.ts`: L985: queryEngineClient.get( "/v1/model-config/codex-openai/oauth/status", )
- `src/lib/api.ts`: L998: queryEngineClient.delete("/v1/model-config/codex-openai/oauth")
- `src/lib/api/repositories-api.ts`: L29: apiClient.get<PaginatedResponse<GitHubRepoSummary>>( "/repos", { params: { provider_key: providerKey, per_page: perPage, cursor: cursor ?? undefined, filterValues, }, }, )
- `src/lib/api/repository-provider-api.ts`: L17: apiClient.get<RepositoryProvidersResponse>( "/repository-providers", )
- `src/lib/api/repository-provider-api.ts`: L67: apiClient.post<IngestTokenResponse>( "/ingest-token", null, { params: queryParams, headers: { Authorization: `Bearer ${patToken}`, }, }, )
- `src/lib/api/tool-config-api.ts`: L19: queryEngineClient.get("/v1/tool-config")
- `src/lib/api/tool-config-api.ts`: L32: queryEngineClient.get(`/v1/tool-config/${provider}`)
- `src/lib/api/tool-config-api.ts`: L55: queryEngineClient.put( `/v1/tool-config/${provider}`, null, { headers: { Authorization: `Bearer ${sanitizedApiKey}` }, }, )
- `src/lib/api/tool-config-api.ts`: L73: queryEngineClient.delete( `/v1/tool-config/${provider}`, )

## Bidirectional Constructs

### realtime_sync (@tanstack/react-db)

- `src/features/repository-agent-snapshots/hooks.ts`: L133: useLiveInfiniteQuery( (q) => q .from({ events: collection }) .orderBy(({ events }) => events.event_id, "desc"), { pageSize, }, [scope.owner, scope.repository, scope.runId, normalizedCodebaseName, pageSize], )
- `src/features/repository-agent-snapshots/hooks.ts`: L64: useLiveQuery( (q) => { if (!collection) { return undefined; } return q.from({ snapshots: collection }); }, [collection], )
- `src/features/repository-agent-snapshots/hooks.ts`: L96: useLiveQuery( (q) => { if (!collection) { return undefined; } return q .from({ progress: collection }) .orderBy(({ progress }) => progress.codebase_name, "asc"); }, [collection], )

## Internal Constructs

### key_value_store.store_definition (zustand)

- `src/features/agent-feedback/store.ts`: L59: create<AgentFeedbackState>()
- `src/features/app-feedback/store.ts`: L10: create<AppFeedbackSheetState>()
- `src/stores/useAuthStore.ts`: L11: create<AuthState>()
- `src/stores/useCommandPaletteStore.ts`: L10: create<CommandPaletteState>()
- `src/stores/useDevModeStore.ts`: L9: create<DevModeState>()
- `src/stores/useThemeStore.ts`: L11: create<ThemeState>()
