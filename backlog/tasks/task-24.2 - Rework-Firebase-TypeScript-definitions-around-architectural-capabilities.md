---
id: TASK-24.2
title: Rework Firebase TypeScript definitions around architectural capabilities
status: To Do
assignee:
  - OpenCode
created_date: '2026-03-30 04:57'
updated_date: '2026-03-30 06:32'
labels:
  - firebase
  - typescript
  - framework-features
milestone: Framework feature architecture
dependencies:
  - TASK-24
references:
  - doc-2
documentation:
  - doc-2
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json
parent_task_id: TASK-24
priority: medium
ordinal: 1300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Revise the Firebase TypeScript feature plan so Firebase APIs map to software-engineering fundamentals rather than raw library-specific names. The rollout should use direct high-confidence capabilities first and leave validator-backed expansion for ambiguous call-expression groups.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Firebase Phase 1 definitions use architecture-level capability naming where the schema supports it.
- [ ] #2 Related Firebase APIs that represent the same software capability are grouped only when the schema can express them safely without losing important semantics.
- [ ] #3 Validator-backed Firebase expansion candidates are identified separately from direct high-confidence capability definitions.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Map Firebase modular SDK APIs into capability families first, not raw API names.
2. Start Phase 1 with high-confidence capability coverage: `app_bootstrap`, `authentication`, `document_db`, and `file_storage`.
3. Model Firebase auth as grouped operations such as `initialize`, `sign_in`, `sign_out`, and `observe_state`; use detector keys or grouped absolute paths for concrete SDK variants like email/password, popup, and redirect flows.
4. Model Firestore and Storage using capability-first operations such as `initialize`, `read`, `write`, `upload`, and `download`.
5. Use grouped `absolute_paths` only when the detectors truly share the same concept, target level, construct query, confidence semantics, and operation meaning.
6. Split ambiguous or weaker call-expression matches into separate low-confidence detectors with explicit `notes` so the existing validator pipeline can confirm, reject, or correct them.
7. Validate the authored definitions against the published v4 docs schema before porting them into ingestion.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Planned against the v4 hierarchy. Firebase definitions should be authored as capability families with operation grouping first; detector keys should capture precise variants only where needed.
<!-- SECTION:NOTES:END -->
