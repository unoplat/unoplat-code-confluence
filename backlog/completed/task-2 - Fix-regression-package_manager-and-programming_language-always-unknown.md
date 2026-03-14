---
id: task-2
title: 'Fix regression: package_manager and programming_language always "unknown"'
status: Done
assignee: []
created_date: '2025-12-12 13:11'
updated_date: '2026-01-06 11:54'
labels:
  - bug
  - regression
  - frontend
  - type-safety
  - zod-schema
dependencies: []
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Problem

Programming language metadata (primary_language, package_manager) is not rendering in the markdown preview - always shows "Unknown" despite backend correctly sending the data.

## Complete Data Flow (with file paths)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. PostgreSQL Table: repository_agent_md_snapshot                       │
│    Column: agent_md_output (JSONB)                                      │
│    Contains: { codebases: { "codebase-name": {                          │
│      programming_language_metadata: { primary_language, package_manager }│
│    }}}                                                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. Electric SQL Sync → TanStack DB Collection                           │
│    File: src/features/repository-agent-snapshots/collection.ts:34-36    │
│    Code: createCollection(electricCollectionOptions({                   │
│            schema: repositoryAgentSnapshotRowSchema, ← PARSES WITH ZOD  │
│          }))                                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. Live Query Hook                                                      │
│    File: src/features/repository-agent-snapshots/hooks.ts:46-57         │
│    Code: const liveQueryResult = useLiveQuery(...)                      │
│          const snapshotRow = liveQueryResult?.data?.[0]                 │
│          const parsedSnapshot = useParsedSnapshot(snapshotRow)          │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. Transformer - Parse Snapshot Row                                     │
│    File: src/features/repository-agent-snapshots/transformers.ts:39-42  │
│    Code: const parsed = repositoryAgentSnapshotRowSchema.parse(row)     │
│    → Calls parseAgentMdOutputs(parsed.agent_md_output)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. ❌ ZOD STRIPS programming_language_metadata HERE                     │
│    File: src/features/repository-agent-snapshots/schema.ts:81-88        │
│    Code: agentMdCodebaseOutputSchema = z.object({                       │
│            codebase_name: z.string(),                                   │
│            statistics: ...,                                             │
│            project_configuration: ...,                                  │
│            development_workflow: ...,                                   │
│            business_logic_domain: ...,                                  │
│            // MISSING: programming_language_metadata ← NOT DEFINED!     │
│          })                                                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. Markdown Renderer (receives data WITHOUT field)                      │
│    File: src/lib/agent-md-to-markdown.ts:21-22                          │
│    Code: agent?.programming_language_metadata?.primary_language ?? "Unknown"
│    Result: Shows "Unknown" because field was stripped by Zod            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Root Cause

**Root Cause**: The `programming_language_metadata` field is **missing from the Zod schema** in `schema.ts:81-88`. Zod's default behavior strips unknown fields during `.parse()`, so the field gets silently removed.

### Backend Model Reference

The backend model (`agent_md_output.py:273-282`) correctly defines:
```python
class ProgrammingLanguageMetadataOutput(BaseModel):
    primary_language: str
    package_manager: str

class AgentMdOutput(BaseModel):
    programming_language_metadata: ProgrammingLanguageMetadataOutput
```

## Implementation Plan

### Step 1: Add `agentMdProgrammingLanguageMetadataSchema` to `schema.ts`

Add after line 79 (before `agentMdCodebaseOutputSchema`):
```typescript
export const agentMdProgrammingLanguageMetadataSchema = z.object({
  primary_language: z.string(),
  package_manager: z.string(),
});

export type AgentMdProgrammingLanguageMetadata = z.infer<
  typeof agentMdProgrammingLanguageMetadataSchema
>;
```

### Step 2: Update `agentMdCodebaseOutputSchema` in `schema.ts`

Add `programming_language_metadata` field:
```typescript
export const agentMdCodebaseOutputSchema = z.object({
  codebase_name: z.string(),
  statistics: z.lazy(() => usageStatisticsSchema).nullish(),
  programming_language_metadata: agentMdProgrammingLanguageMetadataSchema.nullish(), // ADD THIS
  project_configuration: agentMdProjectConfigurationSchema.nullish(),
  development_workflow: agentMdDevelopmentWorkflowSchema.nullish(),
  business_logic_domain: agentMdBusinessLogicSchema.nullish(),
});
```

### Step 3: Run linting and type-check

```bash
task lint-fix FILE_PATH=src/features/repository-agent-snapshots/schema.ts
bunx tsc --noEmit
```

### Step 4: Verify rendering in preview

Test that the preview now shows actual values instead of "Unknown".

## Files to Modify

| File | Change |
|------|--------|
| `src/features/repository-agent-snapshots/schema.ts:79-88` | Add `agentMdProgrammingLanguageMetadataSchema` and include in `agentMdCodebaseOutputSchema` |

## Files Already Correct (No Changes Needed)

| File | Status |
|------|--------|
| `src/lib/agent-md-to-markdown.ts:21-22` | Already uses `agent?.programming_language_metadata?.primary_language` |
| `src/features/repository-agent-snapshots/transformers.ts` | Passes through data correctly |
| `src/features/repository-agent-snapshots/collection.ts` | Uses the schema, will benefit from fix |
| `src/features/repository-agent-snapshots/hooks.ts` | Uses transformers, will benefit from fix |
| `src/components/custom/GenerateAgentsPreview.tsx` | Uses transformed data, will benefit from fix |
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Package manager is correctly detected (e.g., pip, poetry, uv, npm, yarn)
- [x] #2 Programming language is correctly identified for each codebase
- [x] #3 Existing detection logic is restored or fixed
- [x] #4 Root cause of regression is documented
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Steps

1. **Add new Zod schema** for `programming_language_metadata`:
   - Define `agentMdProgrammingLanguageMetadataSchema` with `primary_language` and `package_manager` fields
   - Export the TypeScript type

2. **Update `agentMdCodebaseOutputSchema`**:
   - Add `programming_language_metadata: agentMdProgrammingLanguageMetadataSchema.nullish()`
   - Use `.nullish()` to handle both `null` (from PostgreSQL None) and `undefined` (missing key)

3. **Run validation**:
   - `task lint-fix FILE_PATH=src/features/repository-agent-snapshots/schema.ts`
   - `bunx tsc --noEmit`

4. **Test**:
   - Run dev server and verify preview shows actual language/package manager values
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Investigation Timeline

- **2025-12-16**: Root cause identified using root-cause-investigator agent
- Field was never added to frontend Zod schema when `AgentMdCodebaseOutput` was created
- Backend model has always had this field (`ProgrammingLanguageMetadataOutput` in `agent_md_output.py`)
- Previous implementation may have used SSE types which had the field, but after migration to TanStack DB with schema.ts types, the field was omitted

## Technical Context

- Zod's default behavior strips unknown fields during `.parse()`
- Could use `.passthrough()` to preserve unknown fields, but better to explicitly define the schema for type safety
- The `.nullish()` modifier is used throughout the schema to handle PostgreSQL NULL values and missing keys

## Implementation Complete (2025-12-16)

### Changes Made

**File Modified**: `src/features/repository-agent-snapshots/schema.ts`

1. Added `agentMdProgrammingLanguageMetadataSchema` (lines 81-84):
   ```typescript
   export const agentMdProgrammingLanguageMetadataSchema = z.object({
     primary_language: z.string(),
     package_manager: z.string(),
   });
   ```

2. Added TypeScript type export (lines 86-88):
   ```typescript
   export type AgentMdProgrammingLanguageMetadata = z.infer<
     typeof agentMdProgrammingLanguageMetadataSchema
   >;
   ```

3. Added field to `agentMdCodebaseOutputSchema` (lines 94-95):
   ```typescript
   programming_language_metadata:
     agentMdProgrammingLanguageMetadataSchema.nullish(),
   ```

### Verification
- TypeScript type-check: ✅ Passed (`bunx tsc --noEmit`)
- No new linting errors in schema.ts
<!-- SECTION:NOTES:END -->
