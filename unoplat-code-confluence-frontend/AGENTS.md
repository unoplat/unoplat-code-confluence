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
- **Core dependencies and usage**:
  - **react**: React is a library for web and native user interfaces, letting you build UIs out of components. Usage: create interfaces by composing reusable components, share data/behavior across them, and render UI for web or native targets.
  - **@tanstack/zod-adapter**: Provides a Zod adapter for TanStack Router to validate route search parameters with Zod schemas and handle validation errors in routing flows. Usage: use helpers like `zodValidator` to plug Zod object schemas into a route’s `validateSearch` config and provide defaults for missing or invalid search params.
  - **@radix-ui/react-slider**: A slider input component where the user selects a value from within a given range. Usage: compose `Root`, `Track`, `Range`, and `Thumb` parts; supports controlled/uncontrolled values, multiple thumbs, RTL, and keyboard navigation.
  - **@radix-ui/react-accordion**: A vertically stacked set of interactive headings that each reveal an associated section of content. Usage: build accessible accordions with single/multiple open items, orientation/RTL support, and full keyboard navigation.
  - **class-variance-authority**: A utility for building type-safe UI component variants with traditional CSS class names, reducing manual mapping of classes to props and types. Usage: define base classes and variant mappings with `cva` to generate class strings in TypeScript.
  - **shadcn-ui**: A set of beautifully designed, accessible components and a code distribution platform you copy into your project so you can customize and own the code. Usage: drop in open-code React/TypeScript component templates and customize styles directly.
  - **flyonui**: Open-source Tailwind CSS UI components library with semantic classes and headless JS plugins. Usage: use ready-made components/blocks and optional Tailwind plugin configuration for interactive UI.
  - **react-dom**: Contains methods supported only for web applications that run in a browser DOM environment, serving as the entry point to DOM/server renderers for React. Usage: use `react-dom/client` for roots/hydration, portals, and `react-dom/server` for HTML streaming.
  - **@radix-ui/react-select**: Select displays a list of options triggered by a button. Usage: compose items, labels, groups, and separators with keyboard/typeahead support and configurable positioning.
  - **@radix-ui/react-checkbox**: A control that allows the user to toggle between checked and not checked. Usage: compose `Root` and `Indicator` with optional indeterminate state and keyboard navigation.
  - **@tanstack/query-db-collection**: Integrates TanStack DB collections with TanStack Query so collections can automatically fetch remote data and stay in sync with a query client. Usage: create query-backed collections with optimistic updates, rollback, and persistence hooks.
  - **json2md**: JSON to Markdown converter that transforms structured JSON input into Markdown text output. Usage: convert arrays/objects/strings into headings, lists, tables, links, and custom converters.
  - **@tanstack/electric-db-collection**: Provides an Electric Collection for TanStack DB, integrating with ElectricSQL to enable real-time data synchronization with Postgres. Usage: sync shapes with optimistic updates and configurable persistence handlers.
  - **motion**: Open-source, production-grade animation library for the web that supports JavaScript, React, and Vue. Usage: create high-performance animations and gestures for HTML/CSS/SVG with GPU-accelerated rendering.
  - **@tanstack/react-db**: React adapter for TanStack DB with hooks for live queries. Usage: use `useLiveQuery`/`useLiveInfiniteQuery`/`useLiveSuspenseQuery` for reactive data and paced mutations.
  - **@radix-ui/react-alert-dialog**: A modal dialog that interrupts the user with important content and expects a response. Usage: compose parts like `Root`, `Trigger`, `Content`, `Title`, and `Action` with focus trapping and Escape handling.
  - **@tanstack/react-router**: A powerful, fully type-safe router for React applications with first-class search-params support. Usage: build nested/layout routes with loaders, typed navigation, and automatic prefetching.
  - **@radix-ui/react-slot**: Merges its props onto its immediate child, supporting `asChild` composition. Usage: use `Slot`/`Slottable` to merge props and compose event handlers with child precedence.
  - **@radix-ui/react-collapsible**: An interactive component that expands/collapses a panel. Usage: compose `Root`, `Trigger`, and `Content` with controlled/uncontrolled state and keyboard navigation.
  - **sonner**: An opinionated toast component for React. Usage: mount a `Toaster` and call `toast()` with variants and positioning config.
  - **date-fns**: Toolset for manipulating JavaScript dates in browser and Node.js. Usage: import tree-shakeable functions for formatting, parsing, and date math with immutable helpers.
  - **@tanstack/react-form**: React bindings for TanStack Form, a headless, performant, type-safe form state management library. Usage: use `useForm` and `Field` to manage form state, validation, and submission in custom UIs.
  - **@tanstack/react-table**: Headless UI library for building powerful tables/datagrids. Usage: use `useReactTable` with row models to build custom tables with sorting/filtering/pagination.
  - **@radix-ui/react-avatar**: An image element with a fallback for representing the user. Usage: compose `Avatar.Root`, `Avatar.Image`, and `Avatar.Fallback` with delayed fallback handling.
  - **@radix-ui/react-radio-group**: Checkable button set where only one can be selected. Usage: use `Root`, `Item`, and `Indicator` with orientation control and keyboard navigation.
  - **@mdxeditor/editor**: WYSIWYG markdown editor that accepts/emits markdown strings. Usage: enable features via plugins (headings, links, tables, code blocks) and integrate with Lexical state.
  - **react-day-picker**: React component for date pickers, calendars, and date inputs. Usage: configure selection modes (single/multiple/range), localization, and custom rendering.
  - **@radix-ui/react-toggle-group**: Set of two-state buttons toggled on/off. Usage: build single- or multi-select toggle sets with roving focus and keyboard support.
  - **@radix-ui/react-popover**: Displays rich content in a portal triggered by a button. Usage: compose `Root`, `Trigger`, `Content`, `Portal`, etc., with positioning and focus management.
  - **vaul**: Drawer component for React. Usage: compose `Drawer.Root`, `Trigger`, `Portal`, `Overlay`, and `Content` with snap points and open-state control.
  - **@radix-ui/react-tooltip**: Popup that displays info on hover or focus. Usage: compose `Provider`, `Root`, `Trigger`, `Content`, and `Arrow` with timing/positioning controls.
  - **@radix-ui/react-progress**: Progress indicator for task completion. Usage: compose `Progress.Root` and `Progress.Indicator` with `value`/`max` and ARIA semantics.
  - **nuqs**: Type-safe search params state manager for React. Usage: sync component state with URL query parameters using parsers/serializers.
  - **@dnd-kit/sortable**: Sortable preset for building reorderable lists on top of `@dnd-kit/core`. Usage: use `SortableContext`/`useSortable` with strategies like vertical/horizontal/grid.
  - **@radix-ui/react-dropdown-menu**: Displays a menu triggered by a button. Usage: compose items, labels, submenus, checkable items, and rich positioning with full keyboard nav.
  - **@radix-ui/react-toast**: Succinct, temporary message UI. Usage: use Provider/Viewport with `Root`, `Title`, `Description`, `Action`, and swipe-to-dismiss.
  - **lucide-react**: Implementation of the Lucide icon library for React. Usage: import icon components individually with size/color/stroke props and tree-shaking.
  - **@radix-ui/react-separator**: Visual or semantic separator. Usage: render horizontal/vertical separators with decorative mode for purely visual dividers.
  - **@tanstack/react-query**: Library for asynchronous server-state management and data fetching. Usage: use query/mutation hooks with caching, background updates, and stale data handling.
  - **@dnd-kit/core**: Core drag-and-drop toolkit for React. Usage: wrap in `DndContext` and use draggable/droppable hooks with sensors and modifiers.
  - **canvas-confetti**: Performant confetti animation library for the browser. Usage: call `confetti()` with options for particle count, spread, and colors.
  - **@hugeicons/react**: Hugeicons React wrapper that renders any imported icon. Usage: use `HugeiconsIcon` with size/color/strokeWidth props.
  - **@hugeicons/core-free-icons**: Free core icon package from Hugeicons. Usage: import icons for use with the framework wrapper and customize via component props.
  - **@tanstack/zod-form-adapter**: The Zod adapter for TanStack Form. Usage: connect Zod schemas to TanStack Form’s validation pipeline.
  - **zod**: TypeScript-first validation library for defining schemas. Usage: parse/validate data with static type inference and schema reuse.
  - **@radix-ui/react-tabs**: Layered sections of content displayed one at a time. Usage: compose `Root`, `List`, `Trigger`, and `Content` with keyboard navigation.
  - **@dnd-kit/utilities**: Shared utilities for `@dnd-kit` packages. Usage: import helper utilities with built-in TypeScript declarations.
  - **cmdk**: Fast, unstyled command menu/combobox component. Usage: render `<Command>` with composable items and built-in filtering.
  - **wicg-inert**: Polyfill for the inert attribute/property. Usage: mark DOM subtrees inert to disable interaction and hide from assistive tech.
  - **@radix-ui/react-label**: Accessible label component. Usage: wrap controls or use `htmlFor` to connect labels to inputs.
  - **@radix-ui/react-dialog**: Modal or non-modal dialog primitives. Usage: compose `Root`, `Overlay`, `Content`, and `Close` with focus trapping and Escape dismissal.
  - **@radix-ui/react-toggle**: Two-state button primitive. Usage: use `Toggle.Root` with controlled/uncontrolled pressed state.
  - **clsx**: Utility for constructing `className` strings conditionally. Usage: pass strings/objects/arrays and receive a space-joined class string.
  - **zustand**: Small, scalable state management solution based on hooks. Usage: create stores with actions/middleware and select slices for minimal re-renders.
  - **@tanstack/react-query-devtools**: React Query devtools package. Usage: mount Devtools UI in development builds to inspect query state.
  - **@radix-ui/react-scroll-area**: Custom scroll area primitives. Usage: compose `Root`, `Viewport`, `Scrollbar`, and `Thumb` for styled scrollbars with native scroll behavior.
  - **@tailwindcss/typography**: Tailwind CSS Typography plugin. Usage: apply `prose` classes plus theme modifiers like `prose-invert` and `not-prose`.
  - **axios**: Promise-based HTTP client for browser and Node.js. Usage: use interceptors, cancellation, and data transformation with a Promise API.
  - **@radix-ui/react-switch**: Switch toggle control. Usage: compose `Switch.Root` and `Switch.Thumb` with controlled/uncontrolled state.
  - **nanoid**: Tiny, secure, URL-friendly unique ID generator. Usage: generate short IDs with configurable alphabets/sizes.
  - **react-markdown**: React component to render markdown strings. Usage: render CommonMark safely with remark/rehype plugins and custom component mapping.
  - **tailwind-merge**: Utility to merge Tailwind CSS classes without conflicts. Usage: call `twMerge` to resolve conflicting classes and keep the last applicable class.
  - **next-themes**: Theme abstraction for React apps with dark mode/system preference support. Usage: wrap with `ThemeProvider` and use `useTheme` to sync theme across tabs and SSR.

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
