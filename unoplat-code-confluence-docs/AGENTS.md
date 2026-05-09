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

## Business Logic Domain

The data models describe a documentation website’s content and presentation metadata. They cover configurable announcement banners (messaging, links, variants), changelog entries for product releases (titles, versions, dates, and GitHub release references), and SEO options for pages (title, description, path, and type). Overall, the domain centers on managing a docs site’s release communications, user-facing announcements, and search visibility.

Key data models:
- `src/lib/banner-config.ts`: Announcement banner configuration (messaging, link metadata, and visual variants).
- `src/lib/changelog-utils.ts`: Structured changelog entries (titles, versions, dates, and GitHub release references).
- `src/lib/seo.ts`: SEO metadata for pages (title, description, path, and page type).

Reference details: see `business_logic_references.md`.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `e1d9b8966ae6d91f530e642d0fb01662c3cf2760` (2026-05-09). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `bun install` (working directory: .; config: `package.json` and `bun.lock`)

### Build
- `bun run build` (working directory: .; config: `package.json`)

### Dev
- `bun run dev` (working directory: .; config: `package.json`)

### Test
- `bun run check:framework-definitions` (working directory: .; config: `package.json`)

### Lint
- Not detected

### Type Check
- `bun run types:check` (working directory: .; config: `package.json`)

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This repository backs the Unoplat Code Confluence documentation site for a developer tool focused on code understanding and framework knowledge. Its models center on changelog entries, announcement banners, SEO metadata, a supported-framework catalog, and reusable data-table filtering utilities for browsing that catalog.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
