# AGENTS.md - Frontend Coding Guidelines

## Engineering Workflow
```bash
bun install # ([bun.sh](https://bun.sh/docs/cli/install?utm_source=openai))
bun run build # ([bun.sh](https://bun.sh/docs/cli/run?utm_source=openai))
bun run dev # ([bun.sh](https://bun.sh/docs/cli/run?utm_source=openai))
bun run lint # ([bun.sh](https://bun.sh/docs/cli/run?utm_source=openai))
```

## Dependency Guide
- **Overview**: Full dependency descriptions are maintained in `dependencies_overview.md`.
- **Usage**: Keep this section concise and treat `dependencies_overview.md` as the source-of-truth dependency catalog.

## Business Logic Domain
- **Summary**: This frontend models a Code Confluence platform that connects GitHub/GitLab repositories, collects metadata for ingestion jobs, and tracks workflow runs plus codebase status. It surfaces AI “agent” snapshot outputs (engineering workflows, dependency guides, business logic summaries, app interface scans) and stores user feedback tied to those runs. Supporting domains include credential/provider onboarding, model provider configuration (including OAuth), and tool configuration for integrations.
- **Key domains**:
  - Repository onboarding, provider credential handling, and multi-repository routing/metadata state.
  - Workflow run tracking, agent snapshot storage, and presentation of Agent MD artifacts.
  - Agent MD artifact formatting and markdown conversion for UI display.
  - Model provider configuration, OAuth-based connections, and tool configuration for analysis pipelines.
  - Feedback capture, rating/comment submission, and downstream issue reporting.
- **Key data models & modules**:
  - Agent feedback: `src/features/agent-feedback/api.ts`, `src/features/agent-feedback/schema.ts`, `src/features/agent-feedback/store.ts`, `src/types/agent-feedback.ts`.
  - Agent snapshots & events: `src/features/repository-agent-snapshots/collection.ts`, `src/features/repository-agent-snapshots/hooks.ts`, `src/features/repository-agent-snapshots/schema.ts`, `src/features/repository-agent-snapshots/transformers.ts`, `src/types/agent-events.ts`.
  - Agent MD artifacts: `src/lib/agent-md-to-markdown.ts`.
  - Model configuration & OAuth: `src/features/model-config/provider-schema.ts`, `src/features/model-config/schema-generator.ts`, `src/features/model-config/types.ts`, `src/hooks/useCodexOauth.ts`, `src/hooks/useSaveModelConfig.ts`.
  - Tool configuration: `src/features/tool-config/types.ts`, `src/hooks/useSaveToolConfig.ts`.
  - Repository/provider APIs & routing: `src/lib/api.ts`, `src/lib/api/repositories-api.ts`, `src/lib/api/repository-provider-api.ts`, `src/lib/utils/provider-route-utils.ts`, `src/lib/utils/provider-utils.ts`, `src/types/repository-provider.ts`, `src/routeTree.gen.ts`.
  - Credentials & auth state: `src/lib/validation/credential-schemas.ts`, `src/types/credential-enums.ts`, `src/lib/github-token-utils.ts`, `src/lib/env.ts`, `src/stores/useAuthStore.ts`.
  - UI state & shared types: `src/hooks/use-data-table.ts`, `src/forms/types.ts`, `src/stores/useDevModeStore.ts`, `src/stores/useThemeStore.ts`, `src/types/data-table.ts`, `src/types/index.ts`, `src/types.ts`.
- **Reference**: See `business_logic_references.md` for a detailed index of domain artifacts.

## Commands
```bash
bun install                      # Install dependencies
vite                            # Dev server (http://localhost:5173)
vite build                      # TypeScript check + build
bun eslint .                    # Lint all files
bun eslint src/path/file.tsx    # Lint single file
```

## Code Style (from .cursor/rules)
- **TypeScript**: Use interfaces over types, avoid enums (use maps), no `any` types, precise types always
- **Functions**: Use `function` keyword for pure functions, functional/declarative patterns over classes
- **Naming**: Descriptive with auxiliary verbs (isLoading, hasError), lowercase-with-dashes for directories
- **Imports**: Preserve existing formatting, use `@/*` absolute path alias, use axios for HTTP (never fetch)
- **Formatting**: Preserve existing code/comments unless necessary, curly braces for all conditionals
- **Constraints**: Do not remove code/comments unless necessary, just do what's asked (ask before doing more)

## Architecture
- **Stack**: React 19 + TypeScript + Vite + TanStack Router + TanStack Query + shadcn/ui + TailwindCSS
- **Routing**: TanStack Router (file-based in `src/routes/`), `__root.tsx` redirects `/` to `/onboarding`
- **State**: Zustand (client state), TanStack Query (server state, 5min stale), URL state via `useDataTableWithRouter`
- **UI**: shadcn/ui components use CVA variants as props (`variant="outline"` NOT `variant={{ outline: true }}`)
- **API**: Axios client in `src/lib/api.ts`, wrap all calls in TanStack Query hooks, dual error handling system
- **Forms**: Tanstack Form
- **Tables**: DiceUI + TanStack Table v8 with URL state sync via TanStack Router (NOT nuqs)

## File Structure
`src/components/ui/` shadcn base | `src/components/custom/` business | `src/pages/` pages | `src/routes/` routes | `src/lib/` api/utils/env

## Operating Instructions
1. Use Context7 docs for dependency versions | Check existing code before changes | Structure: exported component → subcomponents → helpers → types
2. When in read mode always remember to raise access from user for any command that you want to execute.

<!-- intent-skills:start -->
# Skill mappings — when working in these areas, load the linked skill file into context.
skills:
  - task: "Using TanStack DB React hooks (useLiveQuery, useLiveSuspenseQuery, useLiveInfiniteQuery, usePacedMutations) for live collections and optimistic updates"
    load: "node_modules/@tanstack/react-db/skills/react-db/SKILL.md"
  - task: "Configuring Electric ShapeStream options for syncing Postgres tables"
    load: "node_modules/@electric-sql/client/skills/electric-shapes/SKILL.md"
  - task: "Designing Postgres schemas and Electric shape WHERE clauses for new synced features"
    load: "node_modules/@electric-sql/client/skills/electric-schema-shapes/SKILL.md"
  - task: "Adding a new real-time synced feature end-to-end with Electric and TanStack DB"
    load: "node_modules/@electric-sql/client/skills/electric-new-feature/SKILL.md"
  - task: "Debugging Electric sync issues (shapes not updating, stale cache, proxy buffering)"
    load: "node_modules/@electric-sql/client/skills/electric-debugging/SKILL.md"
  - task: "Deploying or configuring Electric SQL via Docker or Docker Compose"
    load: "node_modules/@electric-sql/client/skills/electric-deployment/SKILL.md"
  - task: "Setting up server-side Electric proxy routes, CORS headers, or auth for shapes"
    load: "node_modules/@electric-sql/client/skills/electric-proxy-auth/SKILL.md"
  - task: "Securing Postgres for Electric deployment (replication roles, SELECT grants, REPLICA IDENTITY, publication config)"
    load: "node_modules/@electric-sql/client/skills/electric-postgres-security/SKILL.md"
  - task: "Creating or modifying TanStack DB collections with Electric adapter options"
    load: "node_modules/@tanstack/db/skills/db-core/collection-setup/SKILL.md"
  - task: "Writing TanStack DB live queries with the query builder (from, where, join, select, orderBy)"
    load: "node_modules/@tanstack/db/skills/db-core/live-queries/SKILL.md"
  - task: "Adding optimistic mutations to TanStack DB collections (insert, update, delete, transactions)"
    load: "node_modules/@tanstack/db/skills/db-core/mutations-optimistic/SKILL.md"
<!-- intent-skills:end -->
