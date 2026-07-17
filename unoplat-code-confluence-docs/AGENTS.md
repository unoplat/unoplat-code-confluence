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

> Generated from branch `dev` at commit `5ecdba39d57f50c5188a8e32b9dd4f52d01611fe` (2026-07-17). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `bun install` (working directory: repo root; config: `package.json`)

### Build
- `bun run build` (working directory: repo root; config: `package.json`)

### Dev
- `bun run dev` (working directory: repo root; config: `package.json`)

### Test
- `vp test` (working directory: repo root; config: `vite.config.ts`)

### Lint
- `vp check` (working directory: repo root; config: `vite.config.ts`)

### Type Check
- `bun run types:check` (working directory: repo root; config: `package.json`)

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This repository supports the documentation site for Unoplat Code Confluence, a developer tooling product for AI-assisted code understanding and AGENTS.md generation. The data models center on docs-site concerns such as release changelogs, announcement banners, SEO metadata, and framework catalog entries, alongside reusable data-table filtering utilities. The overall domain is product documentation and release communication for a code-context engine aimed at Python and TypeScript codebases.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

## Architecture
See [`architecture.md`](./architecture.md) for the canonical system architecture diagram.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->

<!--VITE PLUS START-->

# Using Vite+, the Unified Toolchain for the Web

This project is using Vite+, a unified toolchain built on top of Vite, Rolldown, Vitest, tsdown, Oxlint, Oxfmt, and Vite Task. Vite+ wraps runtime management, package management, and frontend tooling in a single global CLI called `vp`. Vite+ is distinct from Vite, and it invokes Vite through `vp dev` and `vp build`. Run `vp help` to print a list of commands and `vp <command> --help` for information about a specific command.

Docs are local at `node_modules/vite-plus/docs` or online at https://viteplus.dev/guide/.

## Review Checklist

- [ ] Run `vp install` after pulling remote changes and before getting started.
- [ ] Run `vp check` and `vp test` to format, lint, type check and test changes.
- [ ] Check if there are `vite.config.ts` tasks or `package.json` scripts necessary for validation, run via `vp run <script>`.
- [ ] If setup, runtime, or package-manager behavior looks wrong, run `vp env doctor` and include its output when asking for help.

<!--VITE PLUS END-->
