---
id: TASK-25
title: Fix docs project typecheck and build failures
status: Done
assignee: []
created_date: '2026-03-30 06:52'
updated_date: '2026-03-30 07:00'
labels:
  - docs
  - typescript
  - build
milestone: Docs Stability
dependencies: []
references:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs
documentation:
  - 'TanStack Router docs: file-based routing + generated routeTree.gen'
  - 'TanStack Start docs: route head/loader patterns and server route escaping'
  - 'Fumadocs docs: TanStack Start browser collections + source loader patterns'
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate and resolve current typecheck/build failures in the docs project, preserving existing schema documentation updates while aligning generated artifacts, route typing, and static/generated data handling with the project's Fumadocs and TanStack Router/Start setup.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Docs project typecheck passes without reverting the recent schema documentation changes.
- [x] #2 Docs project build passes with generated/router/static data requirements satisfied.
- [x] #3 Fixes follow current official guidance for the project's documented framework stack and remain minimal in scope.
- [x] #4 A concise report documents root causes, files changed, and verification results.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified official patterns from TanStack Router/Start for importing generated routeTree.gen, exact createFileRoute path matching, route head using loaderData, and escaped-dot server route filenames; verified Fumadocs TanStack Start pattern for createServerFn + browserCollections client loaders + useFumadocsLoader.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fixed docs project typecheck/build failures by restoring generated artifact expectations for framework catalog data, correcting the docs route loader/head typing, and ensuring the generated TanStack route tree is no longer silently ignored. Verified with successful bun run types:check and bun run build.
<!-- SECTION:FINAL_SUMMARY:END -->
