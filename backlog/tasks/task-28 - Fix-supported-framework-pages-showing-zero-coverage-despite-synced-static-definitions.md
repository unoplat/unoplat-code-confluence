---
id: TASK-28
title: >-
  Fix supported framework pages showing zero coverage despite synced static
  definitions
status: In Progress
assignee:
  - pi
created_date: '2026-04-09 10:55'
updated_date: '2026-04-09 11:55'
labels: []
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate the docs supported-framework pages where selecting a framework shows zero coverage rows even though the static framework definition assets are synced. Determine whether the issue is caused by the docs page copy/UI expecting the wrong payload shape, stale generated assets, or a mismatch between the JSON structure and the catalog component, then update the docs implementation so framework pages render the published coverage correctly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Supported framework detail pages load the matching static framework definition asset and render non-zero coverage rows when definitions exist.
- [ ] #2 The docs UI handles the actual published JSON shape for framework definitions instead of incorrectly treating populated payloads as empty.
- [ ] #3 Relevant docs/static asset validation is run and the result is documented in the task notes.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the generated `public/framework-definitions/<language>/<library>.json` assets used by supported-framework pages to confirm the live payload shape and whether synced files contain definitions.
2. Compare that payload shape with `src/components/framework-feature-catalog.tsx` to identify why rendered coverage rows are zero.
3. Update the docs catalog component to read the current framework-definition structure (`capabilities -> operations`) and flatten it into table rows for display.
4. Run docs validation/sync and verify representative pages such as Celery and FastAPI show non-zero rows when definitions exist.
5. Keep the recent copy-only wording changes if they do not conflict, and report the exact root cause plus the minimal code fix.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified root cause: synced framework JSON uses `capabilities -> operations`, while `src/components/framework-feature-catalog.tsx` only read `libraryDefinition.features`, causing zero rendered rows.

Updated `src/components/framework-feature-catalog.tsx` to flatten `capabilities -> operations` into display rows, show an empty-state card only when no definitions exist, and simplify the table by removing the `feature_key` column so `capability` appears first.

Validation run: `cd unoplat-code-confluence-docs && bun run types:check` passed after the UI changes.

Removed the `How to update this page's data` section from supported-framework detail pages because maintenance workflow instructions do not belong on end-user framework reference pages.

Re-ran validation after the docs-page cleanup: `cd unoplat-code-confluence-docs && bun run types:check` passed.

Added a shared `Separator` plus bottom spacing in `src/components/framework-feature-catalog.tsx` so the horizontal table scrollbar no longer visually collides with the docs prev/next navigation cards on short framework pages like Litellm.

Validation run after spacing/separator change: `cd unoplat-code-confluence-docs && bun run types:check` passed.

Lightened the framework table shell by changing the wrapper from `overflow-x-auto rounded-lg border border-fd-border` to `overflow-x-auto pb-2`, keeping horizontal scrolling while removing the heavy boxed container appearance.

Validation run after wrapper cleanup: `cd unoplat-code-confluence-docs && bun run types:check` passed.

Removed the page-level Markdown H1 from all supported-framework detail pages so `DocsTitle` remains the single visible page title and the extra linked heading anchor is no longer rendered below the description.

Removed the `Why this reference exists` / `Why this catalog exists` section across all supported-framework pages to keep the framework reference pages focused on the source-of-truth callout plus current coverage table.

Validation run after framework-page content cleanup: `cd unoplat-code-confluence-docs && bun run types:check` passed.

Removed the remaining page-intro paragraph (`This page provides a static, contributor-friendly view...`) from all supported-framework pages so the pages now go directly from the title/description area to the source-of-truth block and current coverage content.

Validation run after removing intro sections: `cd unoplat-code-confluence-docs && bun run types:check` passed.

Simplified the `Source of Truth` callout across all supported-framework pages by removing the duplicate per-framework `Canonical ... file` bullet, removing the `Docs consume generated static assets from` bullet, and renaming `Canonical definitions live in ingestion` to `Definitions live in ingestion`.

Validation run after source-of-truth cleanup: `cd unoplat-code-confluence-docs && bun run types:check` passed.

Linked the `Deterministic Interface Discovery Schema (DIDS)` phrase inside docs page descriptions to `/docs/contribution/custom-framework-schema` from `src/routes/docs/$.tsx` so pages like Supported Frameworks can deep-link readers to the schema explainer directly from the intro copy.

Added `hideDescription: true` support in `src/routes/docs/$.tsx` and used it on `content/docs/contribution/custom-framework-schema/index.mdx` so the DIDS page keeps its SEO description in frontmatter without rendering the duplicate visible description paragraph under the title.
<!-- SECTION:NOTES:END -->
