# Intuitive Architecture Diagram Review

Use this reference when planning and visually reviewing the rendered PNG for
`architecture.md`. Evidence decides **what** may appear; this reference decides
whether the supported architecture is communicated clearly.

A Mermaid diagram that parses and renders can still fail as documentation. The
reader should be able to understand the main system story before tracing every
edge.

## Intended reading experience

Optimize the diagram for this sequence:

1. Find the initiating consumer or entry point.
2. Follow the primary request or event path through application services.
3. See where state, orchestration, and shared resources support that path.
4. See which external systems exchange data with the application.

Prefer one consistent reading direction—normally left to right, otherwise top to
bottom. Do not make the reader alternate directions or follow a long diagonal
across several role groups.

## Compose the layout before writing edges

- Identify the one-sentence architecture story and place that primary path on a
  straight row or column.
- Place role groups in reading order rather than whichever order source files or
  deployment services were discovered.
- Keep secondary dependencies near the service that uses them and away from the
  primary path when possible.
- Put external systems at the perimeter. Do not place them where their edges cut
  through unrelated groups.
- Keep sibling services aligned when they serve parallel roles.
- Use concise labels that remain readable without awkward wrapping. Prefer a
  short role label in the node and precise details in prose outside the diagram.
- Model a focused system view rather than every proven relationship. Preserve
  material relationships; move low-value detail to prose when including it
  makes the system-level view harder to understand.

## Visual acceptance criteria

Inspect the actual PNG returned by `validate_architecture`; never infer visual
quality from Mermaid source alone. The diagram passes only when all of these are
true:

### Immediate comprehension

- In a three-second scan, the entry point, main application services, persistence
  or orchestration dependencies, and important external systems are identifiable.
- The main path can be traced without backtracking or guessing which edge to
  follow.
- Arrow direction agrees with the chosen reading direction wherever evidence
  allows.

### Geometry and spacing

- Group boundaries do not overlap other groups, services, labels, or unrelated
  edges.
- Service icons and labels do not overlap, clip, or crowd one another.
- Group titles are unobstructed and clearly belong to their boundary.
- No edge passes through an unrelated service icon or label.
- There are no avoidable edge crossings. Parallel edges remain visually
  distinguishable and their arrowheads are visible.
- Spacing is balanced: the diagram does not contain a dense knot beside a large
  empty region caused by a long diagonal layout.

### Semantic legibility

- Each edge has an unambiguous source and destination.
- Bidirectional relationships are distinguishable from two coincident one-way
  arrows.
- The most important path is visually simpler than secondary paths.
- Role grouping helps comprehension rather than merely drawing boxes around a
  tangled graph.

Any overlap, clipped label, hidden arrowhead, edge-through-node, or ambiguous
main flow is a failed visual review even when Mermaid rendering succeeds.

## Mermaid architecture-beta repair tactics

Apply the smallest evidence-preserving repair, render again, and inspect the new
PNG.

1. **Fix reading order first.** Change declaration order and choose ports so the
   primary path uses consistent `R --> L` or `B --> T` relationships.
2. **Separate primary and secondary paths.** Move infrastructure or external
   dependencies to another row or column and connect them from the nearest side.
3. **Use alignment deliberately.** Add `align row` or `align column` only when it
   produces a clearer sibling arrangement in the rendered image.
4. **Shorten labels.** Move implementation detail to prose when wrapping causes
   collisions or excessive node height.
5. **Reduce crossings.** Change ports, reorder siblings, or relocate peripheral
   services. Do not reverse a proven direction merely to improve layout.
6. **Reduce density.** Omit non-material edges from the focused diagram when the
   relationship is already documented in prose or `app_interfaces.md`.
7. **Use a junction only for a real fan-in or fan-out.** A junction may clarify a
   supported shared path, but must not disguise unrelated relationships or invent
   a dispatcher.
8. **Split co-located responsibilities only when evidence supports independent
   runtime nodes.** Do not create fake nodes solely as layout spacers.

## Final visual-review loop

1. Re-read the complete `architecture.md` and the evidence supporting its nodes
   and edges.
2. Call `validate_architecture`; it performs structural validation and returns
   the exact rendered PNG.
3. Inspect the PNG against every acceptance criterion above.
4. If any criterion fails, revise only `architecture.md`, re-render, and inspect
   again.
5. Finish only when the latest digest has both deterministic validation and an
   intuitive visual review. A previous digest does not cover later edits.
