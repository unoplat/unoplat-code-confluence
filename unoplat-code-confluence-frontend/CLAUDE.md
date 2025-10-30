# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Commands

```bash
# Install dependencies
bun install

# Development
vite              # Start dev server at http://localhost:5173

# Build & Deploy
vite build        # TypeScript check + production build
yarn preview      # Preview production build

# Code Quality
bun eslint .                    # Run ESLint on all files
bun eslint src/path/to/file.tsx # Run ESLint on individual file

# Task Runner (alternative)
task dev          # Start development environment
task build        # Build with dependency tracking
task docker       # Build and run Docker container
task outdated     # Review outdated packages (uses bun outdated)
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

### Data Table Architecture (DiceUI + TanStack Table)

The codebase uses **DiceUI Data Table** components built on top of **TanStack Table v8** for all data table implementations. For comprehensive TanStack Table patterns and best practices, see [TanStack Table Documentation](./docs/tanstack_table.md).

Key architecture:

1. **Core Components** (DiceUI-based):
   - `data-table.tsx`: Base table component wrapping TanStack Table with DiceUI styling
   - `data-table-toolbar.tsx`: Standard toolbar with filtering and view options
   - `data-table-advanced-toolbar.tsx`: Advanced toolbar with comprehensive filtering
   - `data-table-filter-list.tsx`: Filter list with AND/OR logic and drag-drop reordering
   - `data-table-filter-menu.tsx`: Command palette-style filter interface
   - `data-table-sort-list.tsx`: Multi-column sorting with drag-drop reordering
   - `data-table-action-bar.tsx`: Floating action bar for selected rows
   - `data-table-pagination.tsx`: Pagination controls with URL state sync
   - `data-table-column-header.tsx`: Column headers with sorting indicators
   - `data-table-view-options.tsx`: Column visibility controls

2. **Custom Hooks**:
   - `useDataTable`: Main hook replacing `nuqs` with TanStack Router for URL state management
   - `useDataTableWithRouter`: Custom wrapper that integrates with TanStack Router search params
   - Manages debouncing (300ms default) and throttling (50ms default) for performance

3. **Filter System**:
   - **Filter Variants**: text, number, range, date, dateRange, boolean, select, multiSelect
   - **Filter Components**:
     - `DataTableFacetedFilter`: For select/multi-select with counts
     - `DataTableDateFilter`: Date picker integration
     - `DataTableSliderFilter`: Range/slider inputs
   - **Column Meta**: Each column defines filter metadata (variant, placeholder, options, etc.)

4. **Table Features**:
   - **Server-side pagination** with cursor-based navigation
   - **Column filtering** with multiple filter types and operators
   - **Multi-column sorting** with visual sort order indicators
   - **Column visibility** controls with view options dropdown
   - **Row selection** with floating action bar
   - **Pinned columns** support via `getCommonPinningStyles`
   - **Loading states** with skeleton rows (10 rows by default)
   - **Keyboard shortcuts**: F (filter), Shift+F (remove last filter), S (sort), Shift+S (remove last sort)

5. **Repository Table Implementation**:
   - Uses `useQuery` with TanStack Query for data fetching
   - Implements cursor-based pagination for GitHub API
   - Pre-fetches next 2 pages for smooth navigation
   - Column definitions include row actions (e.g., "Ingest Repo" button)
   - Integrates with dialog components for row-specific actions
   - Tracks row actions in state for dialog management

6. **State Management**:
   - Table state (pagination, filters, sorting) synced with URL via TanStack Router (NOT nuqs)
   - Filter values persisted in search params for shareable URLs
   - Uses `keepPreviousData` for smooth transitions during pagination
   - Initial state can be set via `initialState` prop

7. **TypeScript Patterns**:
   - Generic `DataTable<TData>` component for type safety
   - Column definitions use `ColumnDef<T>` from TanStack Table
   - Custom column meta interface for DiceUI-specific features
   - Proper typing for filter options, sort states, and row actions

### Shadcn/UI Component Guidelines

Following the official shadcn/ui patterns and registry guidelines:

1. **Component Variant Usage**:
   - **CORRECT**: Use variants directly as props: `<Button variant="outline" size="sm">`
   - **INCORRECT**: Don't pass custom variant objects: `<Button variant={{ outline: true }}`
   - **CORRECT**: Use className for additional styling: `<Button variant="outline" className="w-full">`

2. **Inline Component Definitions**:
   - **Components use CVA (Class Variance Authority)** for variant management
   - **Variants are defined inline** within the component using `cva()` function
   - **Example Pattern**:
     ```tsx
     const buttonVariants = cva(
       "base-classes",
       {
         variants: {
           variant: {
             default: "bg-primary text-primary-foreground",
             outline: "border border-input bg-background"
           },
           size: {
             default: "h-10 px-4 py-2",
             sm: "h-9 px-3",
             lg: "h-11 px-8"
           }
         },
         defaultVariants: {
           variant: "default",
           size: "default"
         }
       }
     )
     ```

3. **Registry Patterns**:
   - **Theme and Style definitions are inline** in JSON registry items
   - **CSS variables** defined using `cssVars` object with `light`, `dark`, and `theme` keys
   - **Component styling** uses design tokens via CSS variables
   - **No external file references** for themes/styles (follow registry schema)

4. **Design Token Usage**:
   - **Colors**: Use semantic tokens like `--background`, `--foreground`, `--primary`
   - **Radius**: Use `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`
   - **Shadows**: Use `--shadow-sm`, `--shadow`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`
   - **Fonts**: Use `--font-sans`, `--font-serif`, `--font-mono`

5. **Component Composition Patterns**:
   - **Import all related components**: `import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"`
   - **Use compound components**: Dialog + DialogContent + DialogHeader pattern
   - **Maintain component hierarchy**: Proper nesting and composition

6. **TypeScript Integration**:
   - **Use VariantProps**: `interface ButtonProps extends VariantProps<typeof buttonVariants>`
   - **Extend HTML attributes**: `React.ButtonHTMLAttributes<HTMLButtonElement>`
   - **Forward refs properly**: Use React.forwardRef for DOM access

7. **Theme Implementation**:
   - **OKLCH color space** for better color manipulation and consistency
   - **CSS variables in :root and .dark** selectors
   - **Tailwind CSS integration** via `@theme inline` directive (v4) or config extension

### Environment Configuration

- API base URL configured via `VITE_UNOPLAT_CODE_CONFLUENCE_API_BASE_URL`
- TypeScript path alias: `@/*` maps to `./src/*`
- Requires Node.js >= 20.0.0
- Uses Bun 1.3.1+ for package management