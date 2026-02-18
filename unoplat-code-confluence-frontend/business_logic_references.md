# Business Logic References

## Platform scope
- Connects source code repositories (GitHub/enterprise providers), ingests metadata, and tracks workflow runs plus multi-codebase analysis status.
- Surfaces AI agent outputs (engineering workflow, dependency guide, business logic, app interfaces) with snapshot storage and feedback/issue submission flows.
- Supports credential/token management, provider onboarding, model/LLM configuration (including OAuth), tool configuration, and artifact formatting.

## Core feature areas and artifacts

### Agent feedback and issue submission
- `src/features/agent-feedback/api.ts`
- `src/features/agent-feedback/schema.ts`
- `src/features/agent-feedback/store.ts`
- `src/types/agent-feedback.ts`

### Agent MD artifact formatting
- `src/lib/agent-md-to-markdown.ts`

### Repository agent snapshots
- `src/features/repository-agent-snapshots/collection.ts`
- `src/features/repository-agent-snapshots/hooks.ts`
- `src/features/repository-agent-snapshots/schema.ts`
- `src/features/repository-agent-snapshots/transformers.ts`
- `src/types/agent-events.ts`

### Model/LLM configuration and OAuth
- `src/features/model-config/provider-schema.ts`
- `src/features/model-config/schema-generator.ts`
- `src/features/model-config/types.ts`
- `src/hooks/useCodexOauth.ts`
- `src/hooks/useSaveModelConfig.ts`

### Tool configuration
- `src/features/tool-config/types.ts`
- `src/hooks/useSaveToolConfig.ts`

### Repository/provider APIs and routing
- `src/lib/api.ts`
- `src/lib/api/repositories-api.ts`
- `src/lib/api/repository-provider-api.ts`
- `src/lib/utils/provider-route-utils.ts`
- `src/lib/utils/provider-utils.ts`
- `src/types/repository-provider.ts`
- `src/routeTree.gen.ts`

### Credentials, auth, and environment
- `src/lib/validation/credential-schemas.ts`
- `src/types/credential-enums.ts`
- `src/lib/github-token-utils.ts`
- `src/lib/env.ts`
- `src/stores/useAuthStore.ts`

### UI state, forms, and shared types
- `src/hooks/use-data-table.ts`
- `src/types/data-table.ts`
- `src/forms/types.ts`
- `src/stores/useDevModeStore.ts`
- `src/stores/useThemeStore.ts`
- `src/types.ts`
- `src/types/index.ts`