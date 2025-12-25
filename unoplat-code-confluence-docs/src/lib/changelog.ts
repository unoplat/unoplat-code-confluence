/**
 * Server-only changelog utilities
 * This file imports from fumadocs-mdx server modules and should only be
 * dynamically imported inside server functions, not at the top level of routes.
 */
import { changelogSource } from "@/lib/source";

// Re-export client-safe types and utilities
export type { ChangelogEntry } from "@/lib/changelog-utils";
export { formatReleaseDate, toReleaseDate } from "@/lib/changelog-utils";

export function getSortedChangelogPages() {
  return changelogSource
    .getPages()
    .filter((page) => page.slugs.length === 1 && page.slugs[0])
    .sort((a, b) => {
      // Primary sort: by releaseDate descending (latest first)
      const dateA = new Date(a.data.releaseDate as string).getTime();
      const dateB = new Date(b.data.releaseDate as string).getTime();
      if (dateB !== dateA) {
        return dateB - dateA;
      }
      // Secondary sort: by version descending (higher version first)
      const versionA = a.data.version as string;
      const versionB = b.data.version as string;
      return versionB.localeCompare(versionA, undefined, { numeric: true });
    });
}
