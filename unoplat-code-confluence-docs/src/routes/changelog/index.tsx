import { createFileRoute } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";
import { staticFunctionMiddleware } from "@tanstack/start-static-server-functions";
import { HomeLayout } from "fumadocs-ui/layouts/home";
import { Rss } from "lucide-react";

import { changelogSource } from "@/lib/source";
import { baseOptions } from "@/lib/layout.shared";
import { ChangelogCard } from "@/components/changelog-card";
import { Button } from "@/components/ui/button";

interface ChangelogEntry {
  slug: string;
  title: string;
  description: string;
  version: string;
  releaseDate: string;
  githubRelease?: string;
}

const serverLoader = createServerFn({ method: "GET" })
  .middleware([staticFunctionMiddleware])
  .handler(async (): Promise<ChangelogEntry[]> => {
    const pages = changelogSource
      .getPages()
      .filter((page) => page.slugs.length === 1 && page.slugs[0]);
    return pages
      .map((page) => ({
        slug: page.slugs[0] ?? "",
        title: page.data.title as string,
        description: page.data.description as string,
        version: page.data.version as string,
        releaseDate: page.data.releaseDate as string,
        githubRelease: page.data.githubRelease as string | undefined,
      }))
      .sort(
        (a, b) =>
          new Date(b.releaseDate).getTime() - new Date(a.releaseDate).getTime(),
      );
  });

export const Route = createFileRoute("/changelog/")({
  component: ChangelogListPage,
  loader: async () => serverLoader(),
});

function ChangelogListPage() {
  const releases = Route.useLoaderData();

  return (
    <HomeLayout {...baseOptions()}>
      <div className="container mx-auto max-w-4xl px-4 sm:px-6 py-12">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold">Changelog</h1>
            <p className="text-fd-muted-foreground">
              Track all releases and updates to Unoplat Code Confluence.
            </p>
          </div>
          <Button variant="outline" size="sm" asChild className="self-start sm:self-auto">
            <a
              href="/changelog/feed/xml"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Rss />
              RSS Feed
            </a>
          </Button>
        </div>

        <div className="space-y-6">
          {releases.map((release) => (
            <ChangelogCard key={release.slug} release={release} />
          ))}
        </div>

        {releases.length === 0 && (
          <div className="text-center py-12 text-fd-muted-foreground">
            No releases yet. Check back soon!
          </div>
        )}
      </div>
    </HomeLayout>
  );
}
