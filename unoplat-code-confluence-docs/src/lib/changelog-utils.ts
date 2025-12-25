/**
 * Client-safe changelog utilities
 * These functions don't import server-only code and can be used in browser context
 */

export interface ChangelogEntry {
  slug: string;
  title: string;
  description: string;
  version: string;
  releaseDate: string;
  githubRelease?: string;
}

export function formatReleaseDate(releaseDate: string): string | null {
  const parsed = Date.parse(releaseDate);
  if (Number.isNaN(parsed)) return null;
  return new Date(parsed).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function toReleaseDate(releaseDate: string): Date | null {
  const parsed = Date.parse(releaseDate);
  if (Number.isNaN(parsed)) return null;
  return new Date(parsed);
}
