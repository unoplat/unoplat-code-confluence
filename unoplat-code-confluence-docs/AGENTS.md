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
