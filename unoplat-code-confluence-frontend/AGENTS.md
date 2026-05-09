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
## Skill Loading

Before substantial work:
- Skill check: run `npx @tanstack/intent@latest list`, or use skills already listed in context.
- Skill guidance: if one local skill clearly matches the task, run `npx @tanstack/intent@latest load <package>#<skill>` and follow the returned `SKILL.md`.
- Monorepos: when working across packages, run the skill check from the workspace root and prefer the local skill for the package being changed.
- Multiple matches: prefer the most specific local skill for the package or concern you are changing; load additional skills only when the task spans multiple packages or concerns.
<!-- intent-skills:end -->

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `e1d9b8966ae6d91f530e642d0fb01662c3cf2760` (2026-05-09). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `bun install` — repository root; config: `package.json`, `bun.lock`

### Build
- `bun run build` — repository root; config: `package.json` (`tsc -b && vite build`)

### Dev
- `bun run dev` — repository root; config: `package.json` (`vite`)

### Test
- Not detected

### Lint
- `bun run lint` — repository root; config: `package.json`

### Type Check
- `bunx tsc -b` — repository root; config: `tsconfig.json`

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This frontend is for a code analysis and repository operations platform centered on onboarding GitHub/GitLab repositories, ingesting them into workflow runs, and displaying AI agent snapshot outputs such as engineering workflows, dependency guides, business logic summaries, and app interface scans. It also covers model-provider and tool configuration, OAuth and credential handling, and feedback flows that turn app or agent feedback into GitHub issues.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
