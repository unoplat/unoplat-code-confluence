# AGENTS.md - Frontend Coding Guidelines

## Commands
```bash
bun install                      # Install dependencies
bun run dev                      # Dev server
bun run build                    # Build
bun run lint                     # Lint
```

## Project Metadata
- **Language**: TypeScript
- **Package manager**: Bun

## Code Style (from .cursor/rules)
- **TypeScript**: Use interfaces over types, avoid enums (use maps), no `any` types, precise types always
- **Functions**: Use `function` keyword for pure functions, functional/declarative patterns over classes
- **Naming**: Descriptive with auxiliary verbs (isLoading, hasError), lowercase-with-dashes for directories
- **Imports**: Preserve existing formatting, use `@/*` absolute path alias, use axios for HTTP (never fetch)
- **Formatting**: Preserve existing code/comments unless necessary, curly braces for all conditionals
- **Constraints**: Do not remove code/comments unless necessary, just do what's asked (ask before doing more)

## Architecture
- **Stack**: React + TypeScript + Vite + TanStack Router + TanStack Query + shadcn/ui + TailwindCSS
- **Routing**: TanStack Router (file-based in `src/routes/`), `__root.tsx` redirects `/` to `/onboarding`
- **State**: Zustand (client state), TanStack Query (server state, 5min stale), URL state via `useDataTableWithRouter`
- **UI**: shadcn/ui components use CVA variants as props (`variant="outline"` NOT `variant={{ outline: true }}`)
- **API**: Axios client in `src/lib/api.ts`, wrap all calls in TanStack Query hooks, dual error handling system
- **Forms**: TanStack React Form + Zod adapters (avoid React Hook Form unless already present)
- **Tables**: DiceUI + TanStack Table v8 with URL state sync via TanStack Router (NOT nuqs)

## Domain Context
- Frontend for a developer platform that connects to source repositories, ingests them, and surfaces Agent MD outputs (workflows, dependency guides, domain summaries, interface catalogs).
- Manages provider credentials/configurations (repo providers, model providers, external tools) including OAuth and API key flows.
- Captures per-repository/per-agent feedback and can open GitHub issues for quality tracking.

## Notable Dependencies
- **Radix UI** primitives (accordion, dialog, tooltip, etc.) for accessible UI building blocks.
- **TanStack** stack (router, query, table, react-form) for routing, data, tables, and forms.
- **Zod** for schema validation, **Zustand** for client state, **Axios** for HTTP.
- **shadcn/ui**, **tailwind-merge**, **class-variance-authority** for styling/design system.

## File Structure
`src/components/ui/` shadcn base | `src/components/custom/` business | `src/pages/` pages | `src/routes/` routes | `src/lib/` api/utils/env

## Operating Instructions
1. Use Context7 docs for dependency versions | Check existing code before changes | Structure: exported component → subcomponents → helpers → types
2. When in read mode always remember to raise access from user for any command that you want to execute.
