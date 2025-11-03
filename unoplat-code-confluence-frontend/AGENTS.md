# AGENTS.md - Frontend Coding Guidelines

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
- **Imports**: Preserve existing formatting, use `@/*` path alias, use axios for HTTP (never fetch)
- **Formatting**: Preserve existing code/comments unless necessary, curly braces for all conditionals
- **Constraints**: Do not remove code/comments unless necessary, just do what's asked (ask before doing more)

## Architecture
- **Stack**: React 19 + TypeScript + Vite + TanStack Router + TanStack Query + shadcn/ui + TailwindCSS
- **Routing**: TanStack Router (file-based in `src/routes/`), `__root.tsx` redirects `/` to `/onboarding`
- **State**: Zustand (client state), TanStack Query (server state, 5min stale), URL state via `useDataTableWithRouter`
- **UI**: shadcn/ui components use CVA variants as props (`variant="outline"` NOT `variant={{ outline: true }}`)
- **API**: Axios client in `src/lib/api.ts`, wrap all calls in TanStack Query hooks, dual error handling system
- **Forms**: React Hook Form + Zod validation, **NOT** TanStack Form
- **Tables**: DiceUI + TanStack Table v8 with URL state sync via TanStack Router (NOT nuqs)

## File Structure
`src/components/ui/` shadcn base | `src/components/custom/` business | `src/pages/` pages | `src/routes/` routes | `src/lib/` api/utils/env

## Key Patterns
Use Context7 docs for dependency versions | Check existing code before changes | Structure: exported component → subcomponents → helpers → types
