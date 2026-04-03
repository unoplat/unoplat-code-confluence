---
id: TASK-24.4.5.1
title: Simplify public schema and docs guidance for single-contract operations
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-04-01 04:55'
updated_date: '2026-04-01 05:33'
labels:
  - framework-features
  - schema
  - docs
milestone: Framework feature architecture
dependencies: []
references:
  - doc-3
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/content/docs/contribution/custom-framework-schema/index.mdx
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/backlog/docs/doc-3
    - Flow-Bridge-v4-Operation-Key-Migration-Design.md
parent_task_id: TASK-24.4.5
priority: high
ordinal: 1511
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the published framework schema guidance and contributor-facing docs so operations are documented as single executable runtime contracts. Remove any wording or examples that imply first-class per-operation variants or detector arrays, and document that variants stay out of scope until a concrete need exists.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The published schema and contributor docs consistently describe one operation as one executable runtime contract.
- [x] #2 Docs-side examples and wording do not imply first-class variant or detector-array support within a single operation.
- [x] #3 Contributor guidance explicitly states that future variant support is deferred until a real use case exists.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update the published schema files so the public contract no longer implies first-class variants.
2. Update the contributor guide and examples so materially different contracts are modeled as separate operations rather than grouped under one operation.
3. Record any docs sync/rendering follow-up only if contradictions remain after the direct edits.
4. Verify the final docs contract is traceable back to doc-3 and the no-variants decision.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
This task should list direct edit targets only. Current expected modification files are the two published schema files plus the contributor guide. Broader docs sync/rendering surfaces may need later follow-up if they remain inconsistent after the public-contract wording is updated, but they are not the primary edit targets for this task. Key policy decision remains: do not introduce first-class variants now; each operation should represent one executable runtime contract. Final schema-shape decision: move detector/runtime fields directly onto the operation payload and remove plural detector nesting from the public public contract, because that is the minimal shape that matches doc-3 and avoids implying grouped heterogeneous contracts. Verification completed by parsing both JSON files, confirming the alias and versioned schema files are identical, and reviewing the edited target-file diff. Untouched surfaces outside the three direct edit targets remain a separate follow-up only if rebuild or sync reveals contradictory rendered output.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Flattened the public schema contract so each operation directly carries one executable runtime contract instead of a plural detector nesting.

Aligned both published schema files and updated the contributor guide to state that materially different matching contracts should be modeled as separate operations.

Documented that first-class variant support is deferred until a concrete real-world use case exists.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Published schema alias files are aligned or any intentional difference is documented on the task.
- [x] #2 Contributor examples no longer show grouped multi-contract variants under one operation.
- [x] #3 Docs sync or rendering surfaces that would preserve contradictory examples are reviewed and any remaining follow-up is recorded explicitly.
- [x] #4 The task notes capture the final decision on whether detector fields stay nested or move directly onto the operation payload.
- [x] #5 A reviewer can trace the public contract wording back to doc-3 and the no-variants decision without ambiguity.
<!-- DOD:END -->
