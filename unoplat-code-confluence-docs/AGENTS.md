## Engineering Workflow

### Install
- `bun install` (see [bun install](https://bun.sh/docs/cli/install?utm_source=openai))

### Build
- `bun run build` (see [bun run](https://bun.sh/docs/cli/run?utm_source=openai))

### Development
- `bun run dev` (see [bun run](https://bun.sh/docs/cli/run?utm_source=openai))

### Type Check
- `bun run types:check` (see [bun run](https://bun.sh/docs/cli/run?utm_source=openai))

## Dependency Guide

- **Overview**: Full dependency descriptions are maintained in `dependencies_overview.md`.
- **Usage**: Keep this section concise and treat `dependencies_overview.md` as the source-of-truth dependency catalog.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `a6db7131de30314e9053e74a395ac31be9cb767a` (2026-04-25). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `bun install` (config: `package.json`, working directory: repo root)

### Build
- `bun run build` (config: `package.json`, working directory: repo root)

### Dev
- `bun run dev` (config: `package.json`, working directory: repo root)

### Test
- Not detected

### Lint
- Not detected

### Type Check
- `bun run types:check` (config: `package.json`, working directory: repo root)

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Logic Domain

The codebase primarily models a documentation site for Unoplat Code Confluence, centered on release communications and page metadata: banner announcements, changelog entries, SEO/canonical tags, and TanStack route structure for docs, changelog, and search pages. It also includes a reusable data-table filtering domain for typed column configs, operators, and faceted filtering across text, number, date, and option-based columns.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
