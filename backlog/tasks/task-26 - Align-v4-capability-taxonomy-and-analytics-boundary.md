---
id: TASK-26
title: Align v4 capability taxonomy and analytics boundary
status: In Progress
assignee: []
created_date: '2026-03-31 13:18'
labels:
  - docs
  - schema
  - taxonomy
milestone: DIDS v4
dependencies: []
references:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/capability-list.md
documentation:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/content/docs/contribution/custom-framework-schema/index.mdx
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json
priority: medium
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refine the custom framework schema v4 capability taxonomy so capabilities stay architecture-first and role-explicit, and clarify the boundary between operational telemetry/observability concerns and user or product analytics. This work should align the published schema enums and docs with the revised capability list and make the taxonomy clearer for coding agents and generated architecture documentation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Published v4 capability enums match the revised role-explicit capability taxonomy.
- [ ] #2 Schema/docs clearly distinguish operational telemetry or observability signals from user or product analytics concerns.
- [ ] #3 Examples and guidance no longer imply deprecated capability names such as rest_api or http_server.
- [ ] #4 Any affected latest-schema aliases or mirrored schema files stay consistent with v4 changes.
<!-- AC:END -->
