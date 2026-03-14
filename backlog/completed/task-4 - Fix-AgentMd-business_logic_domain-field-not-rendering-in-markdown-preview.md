---
id: task-4
title: Fix AgentMd business_logic_domain field not rendering in markdown preview
status: Done
assignee: []
created_date: '2025-12-16 05:26'
updated_date: '2026-01-06 11:54'
labels:
  - bug-fix
  - type-safety
  - frontend
dependencies: []
priority: medium
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The `business_logic_domain` data from PostgreSQL/TanStack DB was not rendering in the markdown preview due to a type mismatch between two parallel type systems:

- **Legacy SSE types** (`types/sse.ts`): Used `business_logic` field name
- **Current DB schema types** (`schema.ts`): Uses `business_logic_domain` field name

Data flowed from PostgreSQL → TanStack DB → transformers → markdown converter, but the markdown converter was importing the legacy `AgentMdOutput` type from `types/sse.ts` which expected `business_logic`, while the actual data had `business_logic_domain`.

**Root Cause**: The codebase had migrated from SSE-based real-time streaming to TanStack DB / Electric SQL local-first sync, but the markdown conversion utilities were still using the legacy SSE types.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 business_logic_domain data renders correctly in the markdown preview dialog
- [x] #2 All files use AgentMdCodebaseOutput from schema.ts (not AgentMdOutput from types/sse.ts)
- [x] #3 Unused legacy SSE types are removed from the codebase
- [x] #4 TypeScript compilation passes with no errors
- [x] #5 No new linting errors introduced
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

### Files Modified

1. **`src/lib/agent-md-to-markdown.ts`**
   - Changed import from `types/sse.ts` to `@/features/repository-agent-snapshots/schema`
   - Updated `agentMdOutputToMarkdown` parameter type: `AgentMdOutput` → `AgentMdCodebaseOutput`
   - Updated `codebasesToMarkdown` parameter type: `Record<string, AgentMdOutput>` → `Record<string, AgentMdCodebaseOutput>`
   - Updated field access: `business_logic` → `business_logic_domain`

2. **`src/features/repository-agent-snapshots/transformers.ts`**
   - Removed import of `AgentMdOutput` from `types/sse.ts`
   - Updated `ParsedRepositoryAgentSnapshot.markdownByCodebase` type to `Record<string, AgentMdCodebaseOutput>`
   - Updated `parseAgentMdOutputs` return type
   - Renamed type guard: `isAgentMdOutput` → `isAgentMdCodebaseOutput`
   - Removed unused `codebaseOutputToAgentMdOutput` stub function

3. **`src/components/custom/GenerateAgentsPreview.tsx`**
   - Updated type import to use `AgentMdCodebaseOutput` from `schema.ts`
   - Updated `GenerateAgentsPreviewProps.codebases` type

### File Deleted

4. **`src/types/sse.ts`** - Completely removed
   - Verified no imports from `@/types/sse` existed in codebase
   - All SSE-related types were unused after migration to TanStack DB sync

### Key Insight

The legacy `sse.ts` was designed for Server-Sent Events streaming where the backend pushed real-time events. The current architecture uses TanStack DB / Electric SQL for local-first data sync from PostgreSQL, making the SSE types obsolete. Consolidating on the Zod schemas in `schema.ts` ensures type consistency with the database structure.
<!-- SECTION:NOTES:END -->
