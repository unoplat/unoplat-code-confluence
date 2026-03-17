---
id: TASK-15
title: Keep AGENTS.md sections pointer-only when companion artifacts exist
status: In Progress
assignee: []
created_date: '2026-03-17 10:58'
updated_date: '2026-03-17 13:01'
labels: []
dependencies: []
references:
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.fix-prompts-agents-md/unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.fix-prompts-agents-md/unoplat-code-confluence-query-engine/tests/tools/test_agents_md_updater_output_validator.py
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Tighten the AGENTS.md updater so sections with companion artifacts write only a concise description of the artifact and a link in AGENTS.md, while keeping detailed inventories in the companion files. This prevents business logic, app interfaces, and dependency catalogs from expanding inside AGENTS.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AGENTS updater prompts instruct dependency, business logic, and app interfaces sections to keep AGENTS.md limited to a concise artifact description plus link
- [ ] #2 Detailed content for those sections is directed to the corresponding companion artifact file instead of AGENTS.md
- [ ] #3 Regression tests cover the pointer-only behavior expectations for companion-artifact-backed sections
- [ ] #4 Relevant tests and diagnostics pass after the change
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented the prompt changes in `temporal_agents.py` so companion-artifact-backed sections keep `AGENTS.md` pointer-only. User explicitly said tests are not required for this change, so test work was skipped.
<!-- SECTION:NOTES:END -->
