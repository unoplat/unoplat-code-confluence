import { createFileRoute, notFound, Link } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";
import { DocsLayout } from "fumadocs-ui/layouts/docs";
import { source } from "@/lib/source";
import { useFumadocsLoader } from "fumadocs-core/source/client";
import browserCollections from "fumadocs-mdx:collections/browser";
import {
  DocsBody,
  DocsDescription,
  DocsPage,
  DocsTitle,
} from "fumadocs-ui/layouts/docs/page";
import defaultMdxComponents from "fumadocs-ui/mdx";
import { baseOptions } from "@/lib/layout.shared";
import { RoadmapCard } from "@/components/roadmap-card";
import { RoadmapSection } from "@/components/roadmap-section";
import { Tab, Tabs } from "fumadocs-ui/components/tabs";
import { Accordion, Accordions } from "fumadocs-ui/components/accordion";
import { staticFunctionMiddleware } from "@tanstack/start-static-server-functions";
import { TypeTable } from "fumadocs-ui/components/type-table";
import { ImageZoom } from "fumadocs-ui/components/image-zoom";

// Server function to load page data - runs on server during dev, pre-rendered for static build if static middleware present
const serverLoader = createServerFn({
  method: "GET",
})
  .middleware([staticFunctionMiddleware])
  .inputValidator((slugs: string[]) => slugs)
  .handler(async ({ data: slugs }) => {
    const page = source.getPage(slugs);
    if (!page) throw notFound();
    return {
      pageTree: await source.serializePageTree(source.getPageTree()),
      path: page.path,
    };
  });

export const Route = createFileRoute("/docs/$")({
  component: Page,
  loader: async ({ params }) => {
    const raw = params._splat;
    const slugs = raw && raw.length > 0 ? raw.split("/") : [];
    const data = await serverLoader({ data: slugs });
    await clientLoader.preload(data.path);
    return data;
  },
});

const clientLoader = browserCollections.docs.createClientLoader<Record<string, never>>({
  id: "docs",
  component({ toc, frontmatter, default: MDX }) {
    return (
      <DocsPage toc={toc}>
        <DocsTitle>{frontmatter.title}</DocsTitle>
        <DocsDescription>{frontmatter.description}</DocsDescription>
        <DocsBody>
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
              RoadmapCard,
              RoadmapSection,
              Tab,
              Tabs,
              Accordion,
              Accordions,
              TypeTable,
            }}
          />
        </DocsBody>
      </DocsPage>
    );
  },
});

function Page() {
  const data = Route.useLoaderData();
  const { pageTree } = useFumadocsLoader(data);
  const Content = clientLoader.getComponent(data.path);

  return (
    <DocsLayout
      {...baseOptions()}
      tree={pageTree}
      sidebar={{
        banner: (
          <Link
            to="/docs/$"
            params={{ _splat: "" }}
            className="flex items-center gap-2 p-3 mb-2 hover:bg-fd-accent/50 rounded-lg transition-colors"
          >
            <span className="font-semibold text-fd-foreground">
              Unoplat Code Confluence
            </span>
          </Link>
        ),
        tabs: false,
      }}
    >
      <Content />
    </DocsLayout>
  );
}
