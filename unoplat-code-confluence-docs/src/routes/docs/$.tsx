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
import { BrainCircuit } from "lucide-react";
import { Tab, Tabs } from "fumadocs-ui/components/tabs";
import { Accordion, Accordions } from "fumadocs-ui/components/accordion";
import { staticFunctionMiddleware } from "@tanstack/start-static-server-functions";
import { TypeTable } from "fumadocs-ui/components/type-table";

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

const clientLoader = browserCollections.docs.createClientLoader({
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
            className="flex items-center gap-2 p-3 mb-2 bg-fd-accent/50 hover:bg-fd-accent rounded-lg border border-fd-border transition-colors"
          >
            <BrainCircuit className="h-5 w-5 text-fd-primary" />
            <div>
              <div className="font-semibold text-fd-foreground">
                Unoplat Code Confluence
              </div>
              <div className="text-xs text-fd-muted-foreground">
                Universal Code Context Engine
              </div>
            </div>
          </Link>
        ),
        tabs: false,
      }}
    >
      <Content />
    </DocsLayout>
  );
}
