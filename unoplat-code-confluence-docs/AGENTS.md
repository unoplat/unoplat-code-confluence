<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `a5948971aedbc9c28b0f70964454c7f6a7c4d6da` (2026-08-31). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `bun install` (working directory: repo root; config: `package.json`)

### Build
- `bun run build` (working directory: repo root; config: `package.json`)

### Dev
- `bun run dev` (working directory: repo root; config: `package.json`)

### Test
- `vp test` (working directory: repo root; config: `vite.config.ts`; requires the Vite+ `vp` CLI)

### Lint
- `vp check` (working directory: repo root; config: `vite.config.ts`; runs Vite+ validation including linting; requires the Vite+ `vp` CLI)

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
