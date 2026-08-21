# Hosted D2 icon URL catalogs

These resources index the **Development**, **Technology**, and **Infrastructure** categories published at [icons.d2lang.com](https://icons.d2lang.com/).

## Storage policy

This directory contains URL metadata only. It deliberately does **not** contain or redistribute SVG bytes.

- `development/catalog.json` maps the hosted `dev/` category.
- `technology/catalog.json` maps the hosted `tech/` category.
- `infrastructure/catalog.json` maps the hosted `infra/` category.
- Each entry provides a display label, hosted path, and HTTPS URL suitable for a D2 `icon:` property.
- Together, the three catalogs are the exact hosted-icon allowlist. Select an
  existing `url` value; do not guess filenames or manually add unlisted URLs.

## Runtime requirement

Rendering a D2 diagram that uses these URLs requires outbound internet access to `https://icons.d2lang.com`. Syntax validation does not prove that a remote icon is reachable. During a complete render, D2 fetches the selected SVG and embeds it into the canonical output, leaving the resulting `architecture.svg` self-contained.

Example:

```d2
runtime: Application runtime {
  icon: https://icons.d2lang.com/dev/python.svg
}
```

Do not rewrite catalog entries as local SVG paths unless the project separately approves vendoring and redistribution of the corresponding assets.

## Licensing and trademarks

The D2 documentation describes the hosted collection as free for convenience, but the catalog does not publish one blanket redistribution license or provenance manifest for all assets. Some entries depict third-party products or trademarks and may be governed by their owners' terms.

These catalogs are references to the hosted service, not a grant of rights. Use an icon only for accurate identification in an architecture diagram, do not imply endorsement, and review applicable brand or usage policies when necessary.

## Refreshing the catalogs

From the query-engine package directory:

```bash
uv run python scripts/update_d2_icon_catalog.py
```

The updater fetches only the public catalog index (or reads `--source-file`) and writes deterministic URL-only JSON; it never downloads linked SVG assets. Review additions and removals before committing an update.

## Official references

- [D2 icons and images](https://d2lang.com/tour/icons/)
- [D2 hosted icon catalog](https://icons.d2lang.com/)
