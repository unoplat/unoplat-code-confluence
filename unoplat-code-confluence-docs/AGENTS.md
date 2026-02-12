# AGENTS

## Project overview
- **Primary language**: TypeScript
- **Package manager**: Bun
- **Domain focus**: Documentation site UI and release communications (announcement banner + changelog entries).

## Commands
Run from the repository root:

| Stage | Command | Notes |
| --- | --- | --- |
| Install | `bun install` | Uses `package.json`. |
| Build | `bun run build` | Uses `package.json`. |
| Dev | `bun run dev` | Uses `package.json`. |
| Type check | `bun run types:check` | Uses `package.json`. |

## Key dependencies
- **vite**: Fast dev server and production build tool with HMR and plugin ecosystem.
- **@tailwindcss/postcss**: Tailwind CSS PostCSS integration for generating utility CSS.
- **lucide-react**: Tree-shakable React icon components with typed SVG props.
- **class-variance-authority**: Type-safe class variants for component styling.
- **@radix-ui/react-slot**: Slot primitives for `asChild` composition.
- **tailwind-merge**: Resolves conflicting Tailwind utility classes.
- **@tanstack/react-router-devtools**: Router state devtools for TanStack Router.
- **@tanstack/react-start**: Full-stack React framework with SSR and server functions.
- **fumadocs-ui**: Default UI theme and components for Fumadocs sites.
- **feed**: Generates RSS/Atom/JSON feeds.
- **lucide-static**: Static Lucide icon assets (SVGs, sprites, fonts).
- **@tanstack/start-static-server-functions**: Build-time cached server functions.
- **react**: Component-based UI library.
- **react-dom**: DOM rendering APIs for React.
- **fumadocs-core**: Headless docs components and search integrations.
- **postcss**: CSS transformation tool with plugin ecosystem.
- **@tanstack/react-router**: Type-safe routing and navigation.
- **@radix-ui/react-separator**: Layout separator component.
- **fumadocs-mdx**: MDX content processing for Fumadocs.
- **clsx**: Conditional className utility.

## Notes for agents
- Keep documentation-centric changes aligned with the banner configuration and changelog utilities in `src/lib`.