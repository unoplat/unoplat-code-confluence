import { createElement } from "react";
import { loader } from "fumadocs-core/source";
import { icons } from "lucide-react";
import { docs, changelog } from "fumadocs-mdx:collections/server";
import { toFumadocsSource } from "fumadocs-mdx/runtime/server";

export const source = loader({
  source: docs.toFumadocsSource(),
  baseUrl: "/docs",
  icon(icon) {
    if (!icon) {
      return;
    }

    const Icon = icons[icon as keyof typeof icons];

    if (!Icon) return;

    return createElement(Icon);
  },
});

export const changelogSource = loader({
  source: toFumadocsSource(changelog, []),
  baseUrl: "/changelog",
});
