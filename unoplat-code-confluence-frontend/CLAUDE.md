# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Commands

```bash
# Install dependencies
yarn install

# Development
yarn dev          # Start dev server at http://localhost:5173

# Build & Deploy
yarn build        # TypeScript check + production build
yarn preview      # Preview production build

# Code Quality
yarn lint         # Run ESLint

# Task Runner (alternative)
task dev          # Start development environment
task build        # Build with dependency tracking
task docker       # Build and run Docker container
```

## Architecture Overview

This is a React 19 + TypeScript SPA built with Vite, using TanStack Router for file-based routing and TanStack Query for server state management.

### Key Architectural Decisions

1. **Routing**: TanStack Router with file-based routing
   - Routes defined in `src/routes/` directory
   - `__root.tsx` redirects `/` to `/onboarding`
   - `_app.tsx` provides the main layout wrapper
   - URL-based state management for data tables (migration in progress)

2. **State Management**:
   - **Zustand** for global client state (`useAuthStore`, `useDevModeStore`)
   - **TanStack Query** for server state with 5-minute stale time
   - **URL State** for data table filters/sorting via `useDataTableWithRouter` hook

3. **UI Components**:
   - **shadcn/ui** components in `src/components/ui/`
   - Custom business components in `src/components/custom/`
   - TailwindCSS for styling with custom design tokens
   - Data tables use TanStack Table with advanced filtering/sorting

4. **API Integration**:
   - Centralized API client in `src/lib/api.ts` using Axios
   - Error handling with dual-type system (API errors vs UI error reports)
   - All API calls wrapped in TanStack Query hooks

5. **Authentication**:
   - GitHub Personal Access Token (PAT) based authentication
   - Token stored in `useAuthStore` with persistence
   - Auth state checked in route guards

### Important Patterns

- **Data Tables**: Use `data-table.tsx` component with column definitions following the pattern in `*-data-table-columns.tsx` files
- **Forms**: Multi-step forms use React Hook Form with Zod validation
- **Error Handling**: Use `error-utils.ts` for standardized error formatting
- **Route State**: Tables and filters sync with URL params via `useDataTableWithRouter`

### Environment Configuration

- API base URL configured via `VITE_UNOPLAT_CODE_CONFLUENCE_API_BASE_URL`
- TypeScript path alias: `@/*` maps to `./src/*`
- Requires Node.js >= 20.0.0
- Uses Yarn 4.8.1 (Berry)