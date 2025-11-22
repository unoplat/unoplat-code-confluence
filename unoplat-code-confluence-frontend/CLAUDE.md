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


### Implementation Instructions

1. Always use absolute imports with alias as mentioned in tsconfig. exmaple- starting with @
2. Post edit run linter and formatter post edit of a single file for that file before proceeding to next file are complete per file with help of below commands:
    # Per-file operations (new capability)
    a. task lint FILE_PATH=src/components/Button.tsx
    b. task lint-fix FILE_PATH=src/pages/HomePage.tsx
    c. task format FILE_PATH=src/lib/api.ts
    d. task format-check FILE_PATH=src/components/ui/dialog.tsx
3. Also ensure when editing multiple portions in a single file first plan using a general agent in terms of what is the outcome and any concerns you see or any advise you need from user. If yes ask user with outcome of the plan and concerns. Once user approves only then proceed to do the edits.
