import { createElement } from "react";
import { loader } from "fumadocs-core/source";
import { icons } from "lucide-react";
import { docs } from "fumadocs-mdx:collections/server";

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
