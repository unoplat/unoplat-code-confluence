# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Documentation Links

**Official shadcn Registry Documentation**: <https://ui.shadcn.com/docs/registry>
- Always refer to this documentation when planning registry modifications
- Use the mcp__context7 tools to fetch latest documentation when needed

**Example Registry Template**: <https://github.com/shadcn-ui/registry-template-v4>
- Reference implementation for best practices 

[**Shadcn Theme Style Guidelines**](shadcn-theme-style-guidelines.md)


## Tool Usage

- Always use context7 for understand anything related to lib or framework before planning or making an edit or suggesting an edit.
- Always use think tool to structure changes and plan.
- Always use web tool to browse similar issues and understand the problem better.


## Commands

```bash
# Install dependencies
pnpm install

# Development
pnpm dev          # Start Next.js dev server with Turbopack at http://localhost:3000

# Build & Deploy
pnpm build        # Build the Next.js application for production
pnpm start        # Start production server
pnpm lint         # Run ESLint

# Registry Management
pnpm registry:build    # Build the shadcn registry using the shadcn CLI
```

## Architecture Overview

This is a **self-hosted shadcn/ui component registry** for the Unoplat Code Confluence design system. It's built as a Next.js 15 application with React 19 and serves as a distribution platform for custom UI components that follow the Unoplat design language.

### Key Architectural Decisions

1. **Registry Structure**: 
   - **shadcn/ui Registry Format**: Components follow the official shadcn registry schema (`registry.json`)
   - **Component Types**: UI components (`registry:ui`), themes (`registry:theme`), styles (`registry:style`), blocks (`registry:block`), and hooks (`registry:hook`)
   - **Path Structure**: All components live under `registry/unoplat-code-confluence/` with organized subdirectories

2. **Component Organization**:
   - **UI Components** (`ui/`): Basic building blocks (button, card, input, etc.) 
   - **Blocks** (`blocks/`): Complex composite components and example implementations
   - **Themes** (`themes/`): Design system theme configuration with CSS variables
   - **Styles** (`styles/`): Complete style system implementation

3. **Design System Implementation**:
   - **Primary Colors**: Blue (#3B82F6), Purple (#8B5CF6), Pink (#F472B6)
   - **Typography**: Inter font family with consistent sizing scale
   - **Component Dependencies**: Uses Radix UI primitives with custom Unoplat styling
   - **Dark Mode**: Full support via CSS variables

4. **Next.js Configuration**:
   - **React 19** with Next.js 15.3.1
   - **Turbopack** for faster development builds
   - **TypeScript** with strict configuration
   - **Tailwind CSS v4** for styling
   - **Component Aliases**: `@/components`, `@/lib/utils`, etc.

### Registry Component Patterns

- **UI Components**: Follow shadcn patterns with Radix UI primitives, using `class-variance-authority` for variants
- **Component Dependencies**: Registry dependencies are resolved automatically by shadcn CLI
- **File Structure**: Each component can include multiple files (`.tsx`, `.css`, hooks, utilities)
- **Showcase Components**: Demo pages that display multiple components together (like `unoplat-showcase`)

### Development Workflow

**IMPORTANT: Component Installation & Usage**

The `components.json` is configured with `"ui": "@/registry/unoplat-code-confluence/ui"` so `pnpm dlx shadcn@latest add [component]` installs directly to the registry.

**✅ CORRECT FLOW**:
```bash
# 1. Install component (goes to registry automatically)
pnpm dlx shadcn@latest add dropdown-menu

# 2. Update registry.json with metadata (if needed)
vi registry.json

# 3. Build registry 
pnpm registry:build

# 4. Use in app
import { DropdownMenu } from "@/registry/unoplat-code-confluence/ui/dropdown-menu"
```

**CRITICAL DESIGN PRINCIPLE**: 
- **ONLY use shadcn elements** - Never manually install non-shadcn dependencies
- All dependencies are managed through the registry system
- Components follow shadcn patterns with Radix UI primitives

- **Component Creation**: Add new components to `registry/unoplat-code-confluence/ui/` or `blocks/`
- **Registry Updates**: Update `registry.json` with new component metadata and dependencies
- **Testing**: Use the development server to preview components in the main app
- **Distribution**: Users install components via `npx shadcn@latest add <component-name>`

### Important Files

- `registry.json`: Central component registry configuration
- `components.json`: shadcn CLI configuration for this registry
- `app/page.tsx`: Showcase page displaying example components
- `registry/unoplat-code-confluence/themes/unoplat-theme.json`: Core design system theme
- `registry/unoplat-code-confluence/styles/unoplat-style.json`: Complete style configuration


## Registry Management

> # Custom shadcn Registry Guidelines
>
> A comprehensive guide for creating and maintaining a custom shadcn registry, based on official documentation.

### Table of Contents
- [Overview & Requirements](#overview--requirements)
- [Getting Started](#getting-started)
- [Real-world Examples](#real-world-examples)
- [registry.json Schema](#registryjson-schema)
- [registry-item.json Schema](#registry-itemjson-schema)
- [FAQ & Troubleshooting](#faq--troubleshooting)
- [Quick-reference Checklist](#quick-reference-checklist)

### Overview & Requirements

- What the registry is – an experimental feature that lets you ship any mix of components, hooks, pages, utilities and other files to any React-based project via the shadcn CLI.
- Absolute requirement – every item you publish must be a valid JSON file that satisfies the registry-item schema.
- Project template – the docs provide a ready-made starter on GitHub if you'd like a scaffold instead of wiring everything by hand.

> **Tip**: The feature is still flagged experimental; expect breaking changes and send feedback to the authors.

---

### Getting Started

#### Bootstrap a registry project
1. Create `registry.json` in your project root and add at least:
   `$schema`, `name`, `homepage`, `items`.
2. Author components anywhere you like, but follow a `registry/<STYLE>/<n>` folder convention (e.g. `registry/new-york/hello-world`).
3. Whitelist those folders in `tailwind.config.ts` → `content: ["./registry/**/*.{js,ts,jsx,tsx}"]`.
4. Declare the item inside `registry.json`, listing its `files` array with `path` and `type`.

#### Build & serve

| Step | Command | Notes |
|------|---------|-------|
| Add CLI | `pnpm add shadcn@canary` | The build feature is only in canary now |
| Script | `"registry:build": "shadcn build"` in package.json | |
| Build | `pnpm registry:build` | JSON files land in public/r by default |
| Serve | `pnpm dev` (Next.js) | Items become http://localhost:3000/r/<ITEM>.json |

#### Publish & secure
- Deploy to any public host (Vercel example shown).
- Simple auth pattern – protect URLs with a `?token=` query param and respond 401 on failure; the CLI honours this automatically.

#### Authoring guidelines (must-dos)
- Place items under `registry/<STYLE>/<n>`
- Required fields for every item: `name`, `description`, `type`, `files`
- List in-registry dependencies under `registryDependencies` (names or full URLs)
- List npm packages under `dependencies` (use name@version when needed)
- Always import local registry code via `@/registry/...`
- Organize source files inside each item into components, hooks, lib, etc.

#### Consuming a remote item

```bash
pnpm dlx shadcn@latest add https://my-host.com/r/hello-world.json
```

---

### Real-world Examples

Each JSON snippet on the docs is a fully valid item—copy, tweak, repeat.

| Item type | Key ideas | Example highlights |
|-----------|-----------|--------------------|
| `registry:style` | Extend shadcn defaults or start from scratch | Declare extra npm deps, import remote items, set cssVars for fonts or new HSL colours |
| `registry:theme` | Pure colour / token bundles | Provide separate light & dark palettes as OKLCH or HSL |
| `registry:block` | Multi-file features | Bundle pages + components; may override primitives by URL-based dependencies |
| CSS variables | Patch Tailwind v4 tokens or add project-wide design tokens | Edit cssVars.theme or per-mode keys |
| Custom CSS | Base styles, component layers, utilities, keyframes | Supply an inline css object with @layer, @utility, @keyframes etc. |
| Utilities & Animations | From simple one-liners to complex patterns | Prefix utilities with @utility, remember to pair animations with cssVars.theme |

---

### registry.json Schema

| Property | Purpose | Example |
|----------|---------|--------|
| `$schema` | JSON-Schema reference | `"https://ui.shadcn.com/schema/registry.json"` |
| `name` | Registry slug (used in data attributes etc.) | `"acme"` |
| `homepage` | Docs / marketing URL | `"https://acme.com"` |
| `items[]` | Array of item objects that each obey the registry-item spec | see registry-item.json schema |

---

### registry-item.json Schema

#### Core fields

| Field | Required | Notes |
|-------|----------|-------|
| `$schema` | ✓ | `"https://ui.shadcn.com/schema/registry-item.json"` |
| `name` | ✓ | Unique within a registry |
| `title` | — | Human-readable heading |
| `description` | — | Longer explanation |
| `type` | ✓ | Controls how the CLI installs the item |
| `files[]` | ✓ | Each entry → path, type, optional target |

#### Supported type values

`registry:block`, `registry:component`, `registry:lib`, `registry:hook`, `registry:ui`, `registry:page`, `registry:file`, `registry:style`, `registry:theme`.

#### Advanced fields
- `author` – free-form "Name <email>".
- `dependencies` – npm packages (name@version optional).
- `registryDependencies` – other registry items, by name (shadcn) or URL.
- `tailwind` – deprecated; prefer cssVars.theme for v4.
- `cssVars` – declare design tokens at theme, light, dark levels.
- `css` – inject raw rules (@layer, @utility, @keyframes, …).
- `docs`, `categories`, `meta` – optional metadata or inline docs.

#### File object details

| Key | Meaning |
|-----|--------|
| `path` | Source path inside the registry project |
| `type` | Must match file's role (e.g. registry:component) |
| `target` | (Pages/files only) where to place it in consuming project; ~ = repo root |

---

### FAQ & Troubleshooting

| Question | Answer / action |
|----------|----------------|
| "What does a complex component look like?" | See full block example with page, two components, hook, util, config file. |
| "How do I add a custom Tailwind color?" | Put the HSL values under cssVars.light and cssVars.dark; the CLI rewrites tailwind.css so you can use bg-brand, text-brand-accent, etc. |
| "How do I override Tailwind theme variables?" | Add or change keys in cssVars.theme, e.g. "text-base": "3rem", "font-heading": "Poppins, sans-serif". |

---

### Quick-reference Checklist
- Create `registry.json` with correct `$schema`.
- For every item: unique `name`, correct `type`, fully listed `files[]`.
- Add `tailwind.config.ts` content glob for the registry folder.
- Provide `registryDependencies` and `dependencies` separately.
- Run `pnpm registry:build` and inspect `public/r/*.json`.
- Test install with `pnpm dlx shadcn add <URL>`.
- Secure endpoints (token or your own auth).
- Keep an eye on docs—feature is experimental!

---

### Further Reading
- Schema download links are embedded in the docs (registry.json and registry-item.json pages) if you want to validate locally with AJV or similar.
- GitHub template and issue tracker for live examples & discussion.
