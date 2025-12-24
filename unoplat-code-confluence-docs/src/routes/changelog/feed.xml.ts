import { createFileRoute } from "@tanstack/react-router";
import { Feed } from "feed";

import { changelogSource } from "@/lib/source";

const SITE_URL = "https://docs.unoplat.io";

function generateFeed(): string {
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

  const pages = changelogSource
    .getPages()
    .filter((page) => page.slugs.length === 1)
    .sort(
      (a, b) =>
        new Date(b.data.releaseDate as string).getTime() -
        new Date(a.data.releaseDate as string).getTime(),
    );

  for (const page of pages) {
    const slug = page.slugs[0];
    if (!slug) continue;
    feed.addItem({
      title: page.data.title as string,
      id: `${SITE_URL}/changelog/${slug}`,
      link: `${SITE_URL}/changelog/${slug}`,
      description: page.data.description as string,
      date: new Date(page.data.releaseDate as string),
    });
  }

  return feed.rss2();
}

export const Route = createFileRoute("/changelog/feed/xml")({
  server: {
    handlers: {
      GET: async () => {
        const xml = generateFeed();
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
