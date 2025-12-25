import { createFileRoute, notFound, Link } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";
import { staticFunctionMiddleware } from "@tanstack/start-static-server-functions";
import { HomeLayout } from "fumadocs-ui/layouts/home";
import browserCollections from "fumadocs-mdx:collections/browser";
import defaultMdxComponents from "fumadocs-ui/mdx";
import { InlineTOC } from "fumadocs-ui/components/inline-toc";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
} from "lucide-react";

import { formatReleaseDate } from "@/lib/changelog-utils";
import { baseOptions } from "@/lib/layout.shared";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface ChangelogNavItem {
  slug: string;
  title: string;
}

interface ChangelogPageData {
  path: string;
  title: string;
  description: string;
  version: string;
  releaseDate: string;
  githubRelease?: string;
  prev: ChangelogNavItem | null;
  next: ChangelogNavItem | null;
}

const serverLoader = createServerFn({ method: "GET" })
  .middleware([staticFunctionMiddleware])
  .inputValidator((slug: string) => slug)
  .handler(async ({ data: slug }): Promise<ChangelogPageData> => {
    if (!slug) throw notFound();

    // Dynamic imports to keep server-only code out of client bundle
    const { changelogSource } = await import("@/lib/source");
    const { getSortedChangelogPages } = await import("@/lib/changelog");

    const slugs = [slug];
    const page = changelogSource.getPage(slugs);
    if (!page) throw notFound();

    const allPages = getSortedChangelogPages();

    const currentIndex = allPages.findIndex(
      (p) => p.slugs.join("/") === slugs.join("/"),
    );

    return {
      path: page.path,
      title: page.data.title as string,
      description: page.data.description as string,
      version: page.data.version as string,
      releaseDate: page.data.releaseDate as string,
      githubRelease: page.data.githubRelease as string | undefined,
      prev:
        currentIndex < allPages.length - 1
          ? {
              slug: allPages[currentIndex + 1].slugs.join("/"),
              title: allPages[currentIndex + 1].data.title as string,
            }
          : null,
      next:
        currentIndex > 0
          ? {
              slug: allPages[currentIndex - 1].slugs.join("/"),
              title: allPages[currentIndex - 1].data.title as string,
            }
          : null,
    };
  });

export const Route = createFileRoute("/changelog/$slug")({
  component: ChangelogPage,
  loader: async ({ params }) => {
    const slug = params.slug;
    const data = await serverLoader({ data: slug });
    await clientLoader.preload(data.path);
    return data;
  },
});

const clientLoader = browserCollections.changelog.createClientLoader({
  id: "changelog",
  component({ toc = [], default: MDX }) {
    return (
      <>
        {toc.length > 0 && (
          <section className="mb-8">
            <InlineTOC items={toc} />
          </section>
        )}
        <section className="prose prose-fd max-w-none">
          <MDX components={defaultMdxComponents} />
        </section>
      </>
    );
  },
});

function ChangelogPage() {
  const data = Route.useLoaderData();
  const Content = clientLoader.getComponent(data.path);

  const formattedDate = formatReleaseDate(data.releaseDate);

  return (
    <HomeLayout {...baseOptions()}>
      <article className="container mx-auto max-w-4xl px-4 sm:px-6 py-12">
        <header className="space-y-6">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/changelog">
              <ArrowLeft />
              Back to Changelog
            </Link>
          </Button>

          <h1 className="text-4xl font-bold">{data.title}</h1>

          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="outline" className="font-mono">
              v{data.version}
            </Badge>
            <Separator orientation="vertical" className="h-4" />
            <time
              dateTime={data.releaseDate}
              className="text-fd-muted-foreground text-sm"
            >
              {formattedDate ?? "Unknown date"}
            </time>
            {data.githubRelease && (
              <>
                <Separator orientation="vertical" className="h-4" />
                <Button variant="link" size="sm" asChild className="h-auto p-0">
                  <a
                    href={data.githubRelease}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink className="size-3.5" />
                    View on GitHub
                  </a>
                </Button>
              </>
            )}
          </div>
        </header>

        <Separator className="my-8" />

        <Content />

        <Separator className="my-8" />

        <nav className="flex justify-between">
          {data.prev ? (
            <Button variant="ghost" asChild>
              <Link to="/changelog/$slug" params={{ slug: data.prev.slug }}>
                <ChevronLeft />
                <span className="flex flex-col items-start">
                  <span className="text-xs text-fd-muted-foreground">
                    Older
                  </span>
                  <span className="font-medium">{data.prev.title}</span>
                </span>
              </Link>
            </Button>
          ) : (
            <span />
          )}
          {data.next ? (
            <Button variant="ghost" asChild>
              <Link to="/changelog/$slug" params={{ slug: data.next.slug }}>
                <span className="flex flex-col items-end">
                  <span className="text-xs text-fd-muted-foreground">
                    Newer
                  </span>
                  <span className="font-medium">{data.next.title}</span>
                </span>
                <ChevronRight />
              </Link>
            </Button>
          ) : (
            <span />
          )}
        </nav>
      </article>
    </HomeLayout>
  );
}
