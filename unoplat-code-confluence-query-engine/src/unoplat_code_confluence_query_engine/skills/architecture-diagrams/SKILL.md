---
name: architecture-diagrams
description: >-
  Author and visually review evidence-based software architecture diagrams as
  D2 v0.7.1 source rendered with ELK to canonical SVG.
---

# D2 Architecture Diagrams

Use this guide to create or review the repository architecture from current,
explicit evidence. The diagram must answer one architectural question clearly;
it is not an exhaustive code inventory.

This skill contains authoring guidance and URL-only icon catalogs. It has no
executable skill scripts. Runtime artifact ownership, console tools, and the
`validate_architecture` finish rule are defined by the agent instructions—follow
those for what you may write and which tools to call. This skill defines how to
author and visually approve `architecture.d2`.

## Source format and render expectations

- Author unfenced D2 only in `architecture.d2`. Do not wrap the source in a
  Markdown document or code fence.
- Target **D2 v0.7.1 with ELK**. The validator owns syntax checks, version
  enforcement, rendering, atomic `architecture.svg` replacement, and digests.
- The only persisted render is SVG. The validator may attach a temporary visual
  preview of the exact generated SVG for review; that preview is not a
  repository artifact and must not be written into the repo.
- Do not judge final layout from D2 source alone. Inspect the validator preview
  against the checklists in this skill. Any source edit after a successful
  validation requires another validate + visual review (see agent finish rule
  and §8 below).

## 1. Build an evidence inventory first

Read every explicitly listed, fresh `app_interfaces.md` artifact. Consult only
the minimal source, configuration, deployment, or infrastructure evidence
needed to confirm a claim. Do not use stale or unlisted interface artifacts and
do not invent components, protocols, dependencies, ownership, or deployment
boundaries.

Before writing D2, record a concise inventory:

- **Nodes:** actors, entry points, deployable applications and services, data
  stores, queues, and external systems.
- **Boundaries:** supported ownership, deployment, trust, network, or subsystem
  boundaries.
- **Relationships:** source, target, semantic direction, action label, and
  interaction type.
- **Scope:** the primary question, abstraction level, and deliberate omissions.
- **Visual vocabulary:** the meaning of shapes, colors, line patterns, and
  icons.

Treat the relationship inventory as a non-regression checklist. Layout or style
changes must never silently remove, merge, reverse, or mislabel an interaction.
Co-location in a deployment file proves membership, not communication.

Model independently meaningful runtime nodes. Omit package directories, shared
source modules, and library-only codebases unless the chosen architectural
question specifically concerns components inside one runtime.

## 2. Keep one abstraction level

Choose one primary level and architectural question:

- **Context:** people and external systems around the system.
- **Container:** independently deployable applications, services, and stores.
- **Component:** important modules inside one application or service.
- **Deployment:** runtime nodes, environments, networks, and infrastructure.
- **Data flow:** production, transformation, persistence, and consumption.

Do not combine all levels in one image. Prefer a focused system-level diagram;
if multiple views are truly required, use D2 boards or composition rather than
crowding unrelated detail together.

Responsibility-oriented container groupings often include consumers and entry
points, repository-owned backend services, platform/infrastructure, and
external services. Create only evidence-backed, non-empty groups. These roles
are useful organization aids, not mandatory decorative boxes.

## 3. Use stable keys and meaningful containers

Separate machine-friendly keys from reader-facing labels. Relationships must
reference keys, including qualified keys across containers:

```d2
client_tier: Client tier {
  web_app: Web application
}

service_tier: Service tier {
  order_api: Order API
}

client_tier.web_app -> service_tier.order_api: submit order
```

Use lower-case stable keys that survive label changes. Keep labels concise and
specific. Use containers only when they communicate ownership, deployment,
trust, runtime, network, or internal/external responsibility. Keep nesting
shallow unless another level adds architectural meaning.

## 4. Establish topology before styling

Add nodes, boundaries, and evidence-backed relationships before colors, icons,
or spacing controls. Select one global direction from the dominant reading
order:

```d2
direction: right

users -> web_app: send requests
web_app -> api: call API
api -> worker: enqueue job
worker -> database: persist result
```

Use `right` when the dominant flow is users → application → dependencies. Use
`down` when it is entry points → processing → persistence. ELK is hierarchical:
nested containers do not have independent flow directions. Render promising
global directions rather than judging layout from source alone.

Declare the dominant semantic flow in the chosen reading direction when
possible. Keep edge labels short, action-oriented, and evidence-backed, such as
`send request`, `publish event`, `read profile`, or `persist result`. Avoid
endpoint-name repetition and prose paragraphs on edges.

Preserve the true semantic arrow direction. If available evidence establishes a
relationship but not direction, do not invent one.

### Reverse and feedback flows

First render the semantically direct edge:

```d2
notification_service -> web_app: send live update
```

A literal reverse edge can create a large loop in a layered layout. Only when it
materially damages readability may you declare the edge in the layout direction
and place the visible arrowhead at its source:

```d2
# Ranked forward for ELK; the visible arrow still points to web_app.
web_app -> notification_service: send live update {
  source-arrowhead: {
    shape: triangle
  }
  target-arrowhead: {
    shape: none
  }
}
```

Use this workaround sparingly. Add an explanatory source comment, inspect the
rendered arrowhead, confirm the visible direction is semantically correct, and
prefer the direct edge whenever its layout is acceptable.

## 5. Define a small semantic visual language

Use a few reusable classes rather than duplicating attributes. Useful edge
semantics are synchronous request, asynchronous event/work, data access or
replication, and external integration:

```d2
classes: {
  service: {
    style: {
      border-radius: 8
      shadow: true
    }
  }
  request: {
    style: {
      stroke: "#2563EB"
      stroke-width: 2
    }
  }
  event: {
    style: {
      stroke: "#7C3AED"
      stroke-width: 2
      stroke-dash: 4
    }
  }
  data: {
    style: {
      stroke: "#B45309"
      stroke-width: 2
    }
  }
  external: {
    style: {
      stroke: "#047857"
      stroke-width: 2
    }
  }
}

api: API {class: service}
worker: Worker {class: service}
api -> worker: publish task {class: event}
```

These colors are examples, not required choices. Meaning must never depend on
color alone: combine color with an action label, dash pattern, arrow style, or
shape. Use object-level overrides only for intentional exceptions.

Keep styling restrained: light container fills, clear borders, consistent leaf
styles, modest rounding or shadows, and hierarchy-appropriate font sizes. Avoid
a unique color or shape for every node. Maintain sufficient contrast and text
size at the expected documentation scale.

## 6. Use only exact catalog icon URLs

Icons are optional recognition aids, not a type system or a substitute for text.
Use them mainly on recognizable leaf nodes such as a database, language, cloud
service, or external product. Prefer a labeled node with an icon; use
`shape: image` only when an icon-only element is genuinely appropriate.

Before adding an icon, call `read_skill_resource` with skill name
`architecture-diagrams` and one of these exact resource names:

- `icons/development/catalog.json` for hosted `dev/` icons
- `icons/technology/catalog.json` for hosted `tech/` icons
- `icons/infrastructure/catalog.json` for hosted `infra/` icons
- `icons/README.md` for storage, runtime, licensing, and refresh policy

Use only an exact HTTPS `url` from a packaged catalog. Never guess a filename,
use an arbitrary host, use a local icon path, or copy and redistribute hosted
SVG bytes. Keep labels beside icons, avoid product logos on broad subsystem
containers, and use a coherent family where practical.

```d2
database: Application database {
  icon: https://icons.d2lang.com/dev/postgresql.svg
}
```

Hosted icons require outbound access to `https://icons.d2lang.com` during the
complete D2 render. Validation alone does not prove reachability. D2 embeds the
fetched icon in the final SVG, so that rendered artifact is self-contained.
If the renderer has no internet access, omit the icon or use a built-in D2 shape
instead of creating a broken reference. Re-render after adding icons because
they change node dimensions and routing.

The catalogs are URL metadata, not a blanket license or trademark grant. Use
third-party marks only for accurate identification, do not imply endorsement,
and follow applicable brand and usage policies.

## 7. Tune spacing last

Wait until nodes, boundaries, relationships, direction, classes, and icons are
stable. Then adjust one concern at a time:

- Increase layer spacing when edge labels are cramped.
- Increase edge-to-node spacing when routes pass too close to nodes.
- Increase container padding when children crowd borders or titles.
- Reduce spacing carefully when the composition is unnecessarily large.

Do not copy unknown ELK flags from another D2 release. The validator controls
the canonical v0.7.1 render. Prefer simple source-level topology and direction
changes; request validator changes separately if a canonical ELK option is
truly required.

## 8. Validate, inspect, and revise

Use this sequence:

1. Build and check the node, boundary, relationship, scope, and vocabulary
   inventory.
2. Choose one abstraction level and one global reading direction.
3. Author the unstyled topology in `architecture.d2`.
4. Correct hierarchy and feedback-flow problems without changing semantics.
5. Add small semantic classes and restrained styling.
6. Load exact icon catalogs and add only useful icons.
7. Tune spacing one concern at a time.
8. Re-read the complete D2 source and compare it with the evidence inventory.
9. Call `validate_architecture` with no arguments.
10. Inspect the attached temporary preview of the exact canonical SVG at full
    resolution and expected embedded size.
11. Repair every structural or visual issue, then re-read, revalidate, and
    inspect again.
12. Load this skill again for final review. Finish only when the latest source
    and render digests correspond to the visually approved artifacts.

Compilation is necessary but not visual approval. Reject a render with
unnecessary crossings, overlapping edges, routes through nodes or labels,
ambiguous label association, excessive bends, dominant reverse-flow loops,
cluttered boundaries, or unreadable text. Never remove or reverse an
architecture fact merely to improve layout.

### Correctness and non-regression

- [ ] Every in-scope node and meaningful boundary is present.
- [ ] Every required relationship remains present and correctly labeled.
- [ ] Visible arrowheads point in the true semantic direction.
- [ ] Containers represent real boundaries rather than decoration.
- [ ] The final topology still matches the evidence inventory.
- [ ] No unsupported component, protocol, dependency, or ownership claim was
      introduced.

### Readability

- [ ] The primary reading order is immediately apparent.
- [ ] Edge labels associate clearly with their relationships.
- [ ] Crossings, bends, and feedback loops are limited.
- [ ] Text remains readable at documentation size.
- [ ] Classes have consistent meanings.
- [ ] Icons improve recognition without replacing labels.

### Accessibility

- [ ] Meaning does not depend only on color.
- [ ] Container fills, borders, labels, and edges have sufficient contrast.
- [ ] Fonts are legible at the intended size.
- [ ] Unfamiliar icons have accompanying text.

## Official references

- [D2 introduction](https://d2lang.com/tour/intro/)
- [D2 containers](https://d2lang.com/tour/containers/)
- [D2 connections and arrowheads](https://d2lang.com/tour/connections/)
- [D2 classes](https://d2lang.com/tour/classes/)
- [D2 styles](https://d2lang.com/tour/style/)
- [D2 icons and images](https://d2lang.com/tour/icons/)
- [D2 layout overview](https://d2lang.com/tour/layouts/)
- [D2 ELK layout](https://d2lang.com/tour/elk/)
- [D2 ELK example gallery](https://d2lang.com/examples/elk/)
- [Eclipse ELK option reference](https://www.eclipse.org/elk/reference.html)
- [D2 hosted icon catalog](https://icons.d2lang.com/)
