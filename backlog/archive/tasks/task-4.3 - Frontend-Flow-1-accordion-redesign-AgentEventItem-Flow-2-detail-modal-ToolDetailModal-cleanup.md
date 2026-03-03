---
id: TASK-4.3
title: >-
  Frontend: Flow 1 accordion redesign (AgentEventItem) + Flow 2 detail modal
  (ToolDetailModal) + cleanup
status: To Do
assignee: []
created_date: '2026-03-02 08:02'
updated_date: '2026-03-02 08:09'
labels:
  - frontend
  - typescript
  - ux
  - react
dependencies:
  - TASK-4.2
references:
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventItem.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/AgentEventsAccordion.tsx
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/ToolResultExpander.tsx
    (DELETE)
  - >-
    unoplat-code-confluence-frontend/src/components/custom/agent-events/ToolDetailModal.tsx
    (NEW)
  - unoplat-code-confluence-frontend/src/types/agent-events.ts
documentation:
  - >-
    Paper design artboard 155-0: Flow 1 — Improved Accordion (click View
    details)
  - 'Paper design artboard X6-0: Flow 2 — Detail Modal (opens on click)'
parent_task_id: TASK-4
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context

This subtask implements the two visual flows from the Paper design:
- **Flow 1** (artboard `155-0`): Redesign event rows in `AgentEventItem.tsx` to show distinct CALL/RESULT rows with a vertical connector line and "View details →" button replacing the broken `[more]` inline expansion.
- **Flow 2** (artboard `X6-0`): New `ToolDetailModal.tsx` that opens when "View details →" is clicked, showing full formatted JSON args and full result content.

This subtask depends on TASK-4.2 (which itself depends on TASK-4.1) and should be executed after TASK-4.2.

## What to Change

### File 1: `AgentEventItem.tsx` — REWRITE per Flow 1

Tool-pair rendering (replace current flat layout):

**CALL row:**
- Indigo filled circle (6px, `bg-indigo-500 rounded-full`)
- `CALL` badge (`text-[10px] font-mono uppercase bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded`)
- Tool name text: `callEvent.tool_name ?? callEvent.message?.replace('Calling ', '')`
- Right-side hint (muted): first value of `callEvent.tool_args` if present (`Object.values(callEvent.tool_args ?? {})[0]`)

**Vertical connector (between CALL and RESULT):**
- `ml-[7px] border-l-2 border-green-400 pl-3 py-0.5` container wrapping the RESULT row
- When pending (no resultEvent): `border-dashed border-green-200`

**RESULT row (resultEvent present):**
- Green filled circle (`bg-green-500 rounded-full`)
- `RESULT` badge (`text-[10px] font-mono uppercase bg-green-50 text-green-700 px-1.5 py-0.5 rounded`)
- 50-char preview: `(resultEvent.tool_result_content ?? resultEvent.message?.replace(/^Tool result: /, '') ?? '').slice(0, 50)`
- `View details →` button (`text-xs text-muted-foreground hover:text-foreground ml-auto`) → calls `onViewDetails?.({ callEvent, resultEvent })`

**Pending RESULT (no resultEvent):**
- Gray spinner icon + `Awaiting result...` text (muted)
- Muted pending row treatment (muted border/background and muted indicator) to match Paper Flow 1

**Single event items:** keep existing rendering logic, no changes.

Remove all references to `ToolResultExpander`.

### File 2 (NEW): `ToolDetailModal.tsx` per Flow 2

Use shadcn `<Dialog>`, `<DialogContent>`, `<DialogHeader>`, `<DialogTitle>`.

```
Header:
  - TOOL CALL badge (indigo, same style as CALL badge)
  - tool name: item?.callEvent?.tool_name ?? item?.callEvent?.message?.replace('Calling ', '')
  - DialogClose X button

ARGUMENTS section:
  - Label "ARGUMENTS" (muted caps, 11px)
  - Copy button → navigator.clipboard.writeText(JSON.stringify(item?.callEvent?.tool_args, null, 2))
  - <pre className="bg-muted rounded p-3 text-xs overflow-auto max-h-[200px]">
      {item?.callEvent?.tool_args
        ? JSON.stringify(item.callEvent.tool_args, null, 2)
        : item?.callEvent?.message ?? '—'}
    </pre>

RESULT section:
  - Label "RESULT" (muted caps, 11px)
  - Source hint: first string path-like value from callEvent.tool_args (check for file_path, path, filepath keys)
  - Copy button → navigator.clipboard.writeText(item?.resultEvent?.tool_result_content ?? '')
  - <pre className="bg-zinc-900 text-zinc-100 rounded p-3 text-xs overflow-auto max-h-[400px]">
      {item?.resultEvent?.tool_result_content
        ?? item?.resultEvent?.message?.replace(/^Tool result: /, '')
        ?? '—'}
    </pre>
```

Export: `export function ToolDetailModal({ open, onOpenChange, item }: ToolDetailModalProps)`

### File 3: `AgentEventsAccordion.tsx` — Add modal state

```typescript
import { useState } from 'react';
import { ToolDetailModal } from '@/components/custom/agent-events/ToolDetailModal';
import type { ToolDetailItem } from '@/types/agent-events';

// Inside component:
const [detailItem, setDetailItem] = useState<ToolDetailItem | null>(null);

// Pass to AgentEventItem:
onViewDetails={setDetailItem}

// Render at accordion level:
<ToolDetailModal
  open={detailItem !== null}
  onOpenChange={(open) => { if (!open) setDetailItem(null); }}
  item={detailItem}
/>
```

### File 4: DELETE `ToolResultExpander.tsx`

File path: `unoplat-code-confluence-frontend/src/components/custom/agent-events/ToolResultExpander.tsx`

Delete entirely. No other file imports it after the AgentEventItem rewrite.

## Key Technical Notes

- Use `z.infer<typeof repositoryAgentEventSchema>` derived type — do not redefine the shape manually
- `Object.values(tool_args ?? {})[0]` for the right-side hint — may be undefined, render nothing if so
- `navigator.clipboard` is available in modern browsers; wrap in try/catch for safety
- All imports top-level, absolute (`@/...`) per CLAUDE.md
- No `any` types — use `Record<string, unknown>` for tool_args in component code
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CALL rows show indigo dot + CALL badge + tool_name (or stripped message fallback) + first tool_args value hint on right
- [ ] #2 RESULT rows show green dot + RESULT badge + 50-char tool_result_content preview (or message fallback) + View details button
- [ ] #3 Vertical green solid border-left line connects CALL row to RESULT row
- [ ] #4 Pending RESULT (no resultEvent) shows dashed connector + Awaiting result... text
- [ ] #5 Clicking View details opens ToolDetailModal
- [ ] #6 ToolDetailModal ARGUMENTS section shows JSON.stringify(tool_args, null, 2) or callEvent.message fallback
- [ ] #7 ToolDetailModal RESULT section shows full tool_result_content in dark code block or message fallback
- [ ] #8 Both Copy buttons copy correct content to clipboard
- [ ] #9 ToolDetailModal renders only when detailItem is non-null (single instance in AgentEventsAccordion)
- [ ] #10 ToolResultExpander.tsx is deleted and not imported anywhere in the codebase
- [ ] #11 bun tsc --noEmit: 0 errors
- [ ] #12 Pending RESULT row uses muted visual treatment (muted indicator + muted bordered/background container) in addition to dashed connector, matching Paper Flow 1 artboard `155-0`.
- [ ] #13 Flow 1 + Flow 2 components prefer shadcn/ui primitives for modal, buttons, badges, and containers; custom primitives are only used when no equivalent shadcn component exists.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 bun tsc --noEmit returns 0 errors
- [ ] #2 Screenshots of running app match Paper artboards 155-0 and X6-0 visually
- [ ] #3 ToolResultExpander.tsx confirmed deleted (no import references found by grep)
- [ ] #4 All acceptance criteria checked
- [ ] #5 Final summary written
- [ ] #6 Pending RESULT row styling is visually verified against Paper `155-0` (dashed connector plus muted pending row treatment).
- [ ] #7 Code review confirms no new UI anti-patterns (for example duplicated modal/button primitives when shadcn equivalents exist).
<!-- DOD:END -->
