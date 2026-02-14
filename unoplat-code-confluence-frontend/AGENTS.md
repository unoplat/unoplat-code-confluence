# AGENTS.md - Frontend Coding Guidelines

## Engineering Workflow
```bash
bun install    # Install dependencies (package.json)
bun run build  # Build (package.json)
bun run dev    # Start dev server (package.json)
bun run lint   # Lint (package.json)
```

## Dependency Guide
- **Package manager**: Bun (`bun install`, `bun run ...`).
Reference File: dependency_guide.md

## Business Logic Domain
- **Summary**: This frontend models a developer tooling platform that ingests GitHub/GitLab-style repositories, stores provider credentials, and kicks off automated repository analysis workflows. It tracks workflow runs, agent snapshot events, and generated Agent MD artifacts (engineering workflow, dependency guide, business domain, app interfaces), while exposing configuration for model providers, auxiliary tools, and OAuth connectivity. It also captures user feedback on agent output and submits structured ratings/comments for issue-tracking follow-up.
- **Key domains**:
  - Repository onboarding, provider credential handling, and multi-repository routing/metadata state.
  - Workflow run tracking, agent snapshot storage, and rendering of Agent MD artifacts.
  - Agent MD artifact formatting and markdown conversion for UI display.
  - Model provider configuration, OAuth-based connections, and tool configuration for analysis pipelines.
  - Feedback capture, rating/comment submission, and downstream issue creation.
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
