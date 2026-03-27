---
id: TASK-22
title: Consolidate alpha/beta badges into single sidebar ALPHA badge
status: Done
assignee: []
created_date: '2026-03-21 06:47'
updated_date: '2026-03-21 07:03'
labels:
  - frontend
  - ui-cleanup
dependencies: []
references:
  - unoplat-code-confluence-frontend/src/components/custom/AppSidebar.tsx
  - unoplat-code-confluence-frontend/src/components/custom/StatusBadge.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/ingested-repositories-data-table-columns.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/RefreshRepositoryDialog.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/DeleteRepositoryDialog.tsx
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace 7 scattered StatusBadge instances across 3 files with a single "ALPHA" badge next to the app logo in the sidebar header. This gives a cleaner UI — inspired by the T3 Code reference design. Design mockups completed in Paper (both dark and light mode artboards) using the codebase's OKLCH design tokens.

## Current state
- `ingested-repositories-data-table-columns.tsx`: 3 StatusBadge usages in dropdown menu items (Generate Agents.md=alpha, Refresh=alpha, Delete=beta)
- `RefreshRepositoryDialog.tsx`: 2 StatusBadge usages (title + inline description)
- `DeleteRepositoryDialog.tsx`: 2 StatusBadge usages (title + inline warning text)

## Target state
- Single `<Badge variant="alpha">` in `AppSidebar.tsx` SidebarHeader, next to logo
- All individual StatusBadge usages removed
- Dialog descriptions rewritten to read naturally without inline badges
- `StatusBadge.tsx` deleted (zero consumers remaining)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Single ALPHA badge visible next to app logo in sidebar header
- [x] #2 Badge hidden when sidebar collapses to icon mode
- [x] #3 Badge works correctly in both light and dark themes
- [x] #4 All 7 individual StatusBadge usages removed from dropdown menus and dialogs
- [x] #5 Dialog descriptions read naturally without inline badge references
- [x] #6 StatusBadge.tsx deleted
- [x] #7 No TypeScript errors (bunx tsc --noEmit passes)
- [x] #8 Lint and format pass on all modified files
<!-- AC:END -->
