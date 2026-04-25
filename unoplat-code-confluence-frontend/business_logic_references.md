# Business Logic References

## Domain Summary
This frontend is centered on a code intelligence/confluence platform that connects GitHub/GitLab repositories, ingests codebases, and tracks workflow runs, repository status, and agent snapshot outputs. It also manages model/provider and tool credentials and OAuth setup, plus app and agent feedback flows that capture ratings, comments, and GitHub issues.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/api.ts#L17-L21` — `AgentRatingPayload`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/api.ts#L27-L35` — `AgentFeedbackSubmissionRequest`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/schema.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/schema.ts#L13-L14` — `SentimentRating`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/schema.ts#L26-L27` — `FeedbackCategory`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/schema.ts#L48-L49` — `AgentSentimentRating`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/store.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/store.ts#L15-L20` — `AgentFeedbackDraft`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/store.ts#L25-L36` — `AgentFeedbackState`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/api.ts#L12-L19` — `AppFeedbackRequest`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/api.ts#L25-L28` — `AppFeedbackResponse`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/schema.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/schema.ts#L18-L19` — `AppFeedbackCategory`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/store.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/store.ts#L3-L8` — `AppFeedbackSheetState`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/provider-schema.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/provider-schema.ts#L65-L67` — `ProviderFieldPrimitive`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/provider-schema.ts#L69-L71` — `ProviderConfigFieldDefinition`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/schema-generator.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/schema-generator.ts#L167-L169` — `ProviderConfigInput`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/types.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/types.ts#L20-L28` — `ProviderFieldType`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/types.ts#L36-L39` — `ProviderFormValues`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L16-L20` — `RepositoryAgentSnapshotScope`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L22-L25` — `RepositoryAgentCodebaseScope`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L140-L142` — `RepositoryAgentSnapshotCollection`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L143-L145` — `RepositoryAgentCodebaseProgressCollection`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L146-L148` — `RepositoryAgentEventCollection`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts#L26-L34` — `UseRepositoryAgentSnapshotResult`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts#L36-L44` — `UseRepositoryAgentCodebaseProgressResult`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts#L46-L56` — `UseRepositoryAgentEventHistoryResult`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L36-L38` — `RepositoryAgentCodebaseProgressRow`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L49-L51` — `AgentMdEngineeringWorkflowCommand`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L57-L59` — `AgentMdEngineeringWorkflow`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L78-L80` — `AgentMdDependencyGuideEntry`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L87-L89` — `AgentMdDependencyGuide`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L95-L97` — `AgentMdInterfaceMatchPattern`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L105-L107` — `AgentMdInterfaceConstruct`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L122-L124` — `AgentMdProgrammingLanguageMetadata`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L200-L202` — `RepositoryAgentSnapshotRow`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/transformers.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/transformers.ts#L10-L13` — `RepositoryAgentCodebaseState`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/transformers.ts#L17-L26` — `ParsedRepositoryAgentSnapshot`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/tool-config/types.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/tool-config/types.ts#L35-L37` — `ToolConfigListResponse`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/forms/types.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/forms/types.ts#L6-L13` — `BaseFieldProps`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/use-data-table.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/use-data-table.ts#L45-L68` — `UseDataTableProps`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useCodexOauth.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useCodexOauth.ts#L10-L14` — `CodexOauthPopupResult`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveModelConfig.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveModelConfig.ts#L9-L12` — `SaveModelConfigVariables`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveModelConfig.ts#L14-L17` — `SaveModelConfigResponse`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveToolConfig.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveToolConfig.ts#L9-L12` — `SaveToolConfigVariables`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveToolConfig.ts#L14-L16` — `DeleteToolConfigVariables`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts#L321-L326` — `AgentGroupSummaryCounts`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/agent-md-to-markdown.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/agent-md-to-markdown.ts#L8-L10` — `AgentMdToMarkdownOptions`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L52-L55` — `ApiResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L58-L60` — `FastApiErrorResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L66-L71` — `ApiError`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L186-L191` — `FetchGitHubRepositoriesParams`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L416-L422` — `GitHubUser`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L500-L510` — `GithubIssueSubmissionRequest`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L515-L521` — `IssueTracking`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L620-L622` — `RepositoryWorkflowRunResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L624-L628` — `RepositoryAgentRunCancelResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L630-L634` — `RepositoryAgentMdPrRequest`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L636-L643` — `RepositoryAgentMdPrResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L645-L648` — `RepositoryAgentMdPrStatusResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L725-L731` — `RepositoryAgentSnapshotResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L736-L740` — `RepositoryAgentSnapshot`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L782-L799` — `ModelConfigResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L801-L804` — `DeleteModelConfigResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L806-L811` — `CodexOAuthAuthorizeResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L813-L815` — `CodexOAuthAuthorizeRequest`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L817-L820` — `CodexOAuthFlowStatusResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L822-L827` — `CodexOAuthStatusResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L829-L832` — `CodexOAuthDeleteResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L837-L842` — `SaveModelConfigRequest`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repositories-api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repositories-api.ts#L5-L10` — `FetchReposParams`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repository-provider-api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repository-provider-api.ts#L31-L33` — `IngestTokenResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repository-provider-api.ts#L35-L38` — `ApiErrorResponse`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/env.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/env.ts#L7-L32` — `Env`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/github-token-utils.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/github-token-utils.ts#L10-L13` — `BuildPatLinkOptions`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/utils/provider-route-utils.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/utils/provider-route-utils.ts#L6-L10` — `ProviderMetadata`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/utils/provider-utils.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/utils/provider-utils.ts#L147-L152` — `ProviderOption`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/validation/credential-schemas.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/validation/credential-schemas.ts#L101-L103` — `RepositoryRequestConfigData`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L85-L97` — `FileRoutesByFullPath`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L98-L109` — `FileRoutesByTo`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L110-L124` — `FileRoutesById`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L125-L166` — `FileRouteTypes`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L167-L172` — `RootRouteChildren`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L175-L260` — `FileRoutesByPath`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L263-L266` — `AppOnboardingRouteChildren`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L277-L284` — `AppRouteChildren`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useAuthStore.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useAuthStore.ts#L5-L9` — `AuthState`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useCommandPaletteStore.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useCommandPaletteStore.ts#L3-L8` — `CommandPaletteState`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useDevModeStore.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useDevModeStore.ts#L4-L7` — `DevModeState`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useThemeStore.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useThemeStore.ts#L6-L9` — `ThemeState`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L4-L10` — `GitHubRepoSummary`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L13-L19` — `RepositoryConfigDialogData`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L22-L27` — `RepositoryMetadata`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L30-L33` — `RepositorySelection`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L36-L41` — `IngestionStatus`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L43-L51` — `IngestionJob`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L53-L56` — `PaginationJson`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L58-L63` — `PaginatedResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L65-L68` — `FlagResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L71-L78` — `ProgrammingLanguageMetadata`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L80-L88` — `CodebaseConfig`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L91-L93` — `CodebaseMetadataResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L96-L102` — `RepositoryRequestConfiguration`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L108-L117` — `CodebaseRepoConfig`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L119-L124` — `GitHubRepoResponseConfiguration`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L126-L128` — `CodebaseStatusSchema`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L135-L138` — `CompletedStage`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L141-L145` — `ApiResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L151-L159` — `JobStatus`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L162-L165` — `RepositoryWorkflowOperation`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L168-L180` — `ParentWorkflowJobResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L183-L185` — `ParentWorkflowJobListResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L190-L196` — `IssueTracking`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L207-L211` — `ApiErrorReport`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L216-L232` — `UiErrorReport`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L235-L242` — `WorkflowRun`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L245-L253` — `FlattenedCodebaseRun`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L256-L259` — `WorkflowStatus`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L262-L265` — `CodebaseStatus`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L268-L270` — `CodebaseStatusList`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L273-L284` — `GithubRepoStatus`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L300-L304` — `IngestedRepository`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L306-L308` — `IngestedRepositoriesResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L311-L316` — `RefreshRepositoryResponse`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L6-L12` — `AgentGroup`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L17-L20` — `AgentEventsAccordionProps`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L25-L28` — `ToolDetailItem`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L33-L37` — `ToolDetailModalProps`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L43-L47` — `AgentEventSingleDisplayItem`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L49-L54` — `AgentEventToolPairDisplayItem`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L56-L58` — `AgentEventDisplayItem`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L63-L66` — `AgentEventItemProps`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L71-L73` — `AgentGroupHeaderProps`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts#L21-L25` — `AgentRating`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts#L30-L39` — `AgentFeedbackFormData`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts#L49-L54` — `SentimentConfig`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts#L83-L86` — `CategoryConfig`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/credential-enums.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/credential-enums.ts#L49-L55` — `CredentialParams`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/credential-enums.ts#L60-L62` — `TokenOperationParams`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L7-L9` — `TableMeta`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L12-L21` — `ColumnMeta`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L24-L30` — `QueryKeys`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L32-L37` — `Option`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L43-L45` — `ExtendedColumnSort`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L47-L49` — `ExtendedColumnFilter`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L51-L54` — `DataTableRowAction`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L1-L13` — `Repository`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L17-L19` — `RepositoryWithCategory`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L21-L26` — `RepositoryMetadata`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L28-L31` — `RepositorySelection`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L33-L38` — `IngestionStatus`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L40-L48` — `IngestionJob`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/repository-provider.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/repository-provider.ts#L6-L8` — `RepositoryProvidersResponse`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/repository-provider.ts#L13-L17` — `RepositoryProviderFormData`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/repository-provider.ts#L22-L26` — `Provider`
