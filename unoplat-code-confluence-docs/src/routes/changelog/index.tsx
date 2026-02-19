import { createFileRoute } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";
import { staticFunctionMiddleware } from "@tanstack/start-static-server-functions";
import { HomeLayout } from "fumadocs-ui/layouts/home";
import browserCollections from "fumadocs-mdx:collections/browser";
import defaultMdxComponents from "fumadocs-ui/mdx";
import { ImageZoom } from "fumadocs-ui/components/image-zoom";

import type { ChangelogEntry } from "@/lib/changelog-utils";
import { baseOptions } from "@/lib/layout.shared";
import { ChangelogLayout } from "@/components/commit-layout/changelog-layout";
import { ChangelogArticle } from "@/components/commit-layout/changelog-article";

const serverLoader = createServerFn({ method: "GET" })
  .middleware([staticFunctionMiddleware])
  .handler(async (): Promise<ChangelogEntry[]> => {
    const { getSortedChangelogPages } = await import("@/lib/changelog");
    const pages = getSortedChangelogPages();
    return pages.map((page) => ({
      slug: page.slugs[0] ?? "",
      path: page.path,
      title: page.data.title as string,
      description: page.data.description as string,
      version: page.data.version as string,
      releaseDate: page.data.releaseDate as string,
      githubRelease: page.data.githubRelease as string | undefined,
    }));
  });

const changelogClientLoader = browserCollections.changelog.createClientLoader<
  Record<string, never>
>({
  id: "changelog-timeline",
  component({ default: MDX }) {
    return (
      <MDX
        components={{
          ...defaultMdxComponents,
          img: (props) => (
            <ImageZoom
              {...props}
              loading="lazy"
              decoding="async"
              className="rounded-lg border border-fd-border my-4"
            />
          ),
        }}
      />
    );
  },
});

export const Route = createFileRoute("/changelog/")({
  component: ChangelogTimelinePage,
  loader: async () => {
    const entries = await serverLoader();
    await Promise.all(
      entries.map((entry) => changelogClientLoader.preload(entry.path)),
    );
    return entries;
  },
});

function ChangelogTimelinePage() {
  const entries = Route.useLoaderData();

  return (
    <HomeLayout {...baseOptions()}>
      <ChangelogLayout>
        {entries.map((entry) => {
          const Content = changelogClientLoader.getComponent(entry.path);
          return (
            <ChangelogArticle
              key={entry.slug}
              id={entry.slug}
              date={entry.releaseDate}
              title={entry.title}
              githubRelease={entry.githubRelease}
            >
              <Content />
            </ChangelogArticle>
          );
        })}
      </ChangelogLayout>
    </HomeLayout>
  );
}
