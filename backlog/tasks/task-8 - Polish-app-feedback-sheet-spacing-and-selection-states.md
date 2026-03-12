---
id: TASK-8
title: Polish app feedback sheet spacing and selection states
status: Done
assignee: []
created_date: '2026-03-06 10:11'
updated_date: '2026-03-10 09:31'
labels:
  - frontend
  - design-polish
dependencies: []
references:
  - >-
    unoplat-code-confluence-frontend/src/features/app-feedback/components/app-feedback-sheet.tsx
  - >-
    unoplat-code-confluence-frontend/src/features/app-feedback/components/feedback-category-selector.tsx
  - unoplat-code-confluence-frontend/src/forms/fields/emoji-rating-field.tsx
  - unoplat-code-confluence-frontend/src/components/ui/sheet.tsx
priority: medium
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Bring the app feedback sheet closer to the Paper design by balancing header/body spacing and improving selected-card hover feedback so the form feels visually even and responsive.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The app feedback sheet header, content spacing, and section rhythm more closely match the Paper design.
- [x] #2 The title/subtitle block reads with balanced spacing instead of an extra gap between the header and form body.
- [x] #3 Selected category and sentiment options retain a clear highlighted hover state.
- [x] #4 Relevant frontend verification passes for the updated feedback sheet components.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Matched the feedback sheet container more closely to the Paper spacing by removing the extra sheet-content gap, tightening header typography, and aligning the close button inset.

Updated category and sentiment toggle cards so hover states preserve and intensify the selected treatment instead of flattening it.

Verified with `bun run build` and targeted `bun eslint` on the changed frontend files.

Follow-up root cause: the feedback sheet was still mixing Paper-tuned blocks with generic shared form primitives. The shared label defaults, generic textarea counter placement, and textarea row sizing created uneven optical rhythm across sections, while the sentiment block looked right because it already used a dedicated layout.

Reworked the app feedback subject and description fields to use local Paper-aligned sizing and moved the character counter into the description header row so section spacing stays consistent.

Used the existing Chrome session to inspect computed layout. Root cause was that the app runs with `html` font-size `20px`, so Tailwind rem-scale utilities like `gap-2`, `px-6`, `py-4`, `text-base`, and `h-5` were rendering larger than the Paper pixel spec inside the feedback sheet.

Converted the feedback sheet spacing, typography, icon sizing, and control padding to explicit pixel-based arbitrary classes where the design must match Paper exactly. Chrome verification after the change shows label-to-control spacing at ~8px for category/subject/description and ~16px for sentiment, matching the Paper layout.

Continuing a line-by-line spacing audit after user feedback that the sheet still feels uneven in the live browser.

Chrome line-by-line audit on the live sheet showed the real visible mismatch: category/subject/description had ~8px from label to control and ~24px to the next label, but sentiment had ~16px from label to first card and ~32px from last card to the next label because the toggle row itself still had extra vertical padding.

Removed the sentiment row vertical padding in the live implementation so all sections now use the same visible rhythm in Chrome: ~8px label-to-control and ~24px control-to-next-label.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Balanced the app feedback sheet header/body spacing to better match the Paper design.

Improved category and sentiment selected-card hover feedback so active options stay visually highlighted.

Passed frontend verification with build and targeted linting.

Identified the remaining spacing issue as a mismatch between shared form primitives and the Paper-specific sheet layout, then replaced the subject/description layout with local Paper-aligned field structure.

Used Chrome DevTools to trace the uneven spacing to the app-wide 20px root font size scaling rem-based Tailwind utilities, then replaced the feedback sheet's Paper-sensitive spacing and typography with explicit pixel values.

Used the live Chrome session to isolate the remaining mismatch to extra vertical padding on the sentiment row, then removed it so all sections now share the same visible spacing rhythm.
<!-- SECTION:FINAL_SUMMARY:END -->
