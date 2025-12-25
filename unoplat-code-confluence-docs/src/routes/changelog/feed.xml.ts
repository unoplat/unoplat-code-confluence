import { createFileRoute } from "@tanstack/react-router";

const SITE_URL = process.env.PUBLIC_SITE_URL ?? "https://docs.unoplat.io";

async function generateFeed(): Promise<string> {
  // Dynamic imports to keep server-only code out of client bundle
  const { Feed } = await import("feed");
  const { getSortedChangelogPages } = await import("@/lib/changelog");
  const { toReleaseDate } = await import("@/lib/changelog-utils");

  const feed = new Feed({
    title: "Unoplat Code Confluence Changelog",
    description: "Release notes and updates for Unoplat Code Confluence",
    id: `${SITE_URL}/changelog`,
    link: `${SITE_URL}/changelog`,
    language: "en",
    copyright: `All rights reserved ${new Date().getFullYear()}, Unoplat`,
    feedLinks: {
      rss2: `${SITE_URL}/changelog/feed/xml`,
    },
    author: {
      name: "Unoplat Team",
      link: SITE_URL,
    },
  });

  const pages = getSortedChangelogPages();

  for (const page of pages) {
    const slug = page.slugs[0];
    if (!slug) continue;
    const releaseDate = toReleaseDate(page.data.releaseDate as string);
    if (!releaseDate) continue;
    feed.addItem({
      title: page.data.title as string,
      id: `${SITE_URL}/changelog/${slug}`,
      link: `${SITE_URL}/changelog/${slug}`,
      description: page.data.description as string,
      date: releaseDate,
    });
  }

  return feed.rss2();
}

export const Route = createFileRoute("/changelog/feed/xml")({
  server: {
    handlers: {
      GET: async () => {
        const xml = await generateFeed();
        return new Response(xml, {
          headers: {
            "Content-Type": "application/xml; charset=utf-8",
            "Cache-Control": "public, max-age=3600",
          },
        });
      },
    },
  },
});
