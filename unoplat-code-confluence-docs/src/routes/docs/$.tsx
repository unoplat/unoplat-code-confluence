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
import { seo, canonicalLink } from "@/lib/seo";

const DIDS_LABEL = "Deterministic Interface Discovery Schema (DIDS)";
const DIDS_DOCS_SLUG = "contribution/custom-framework-schema";

interface DocsPageLoaderData {
  pageTree: Awaited<ReturnType<typeof source.serializePageTree>>;
  path: string;
  url: string;
  title: string;
  description: string;
}

// Server function to load page data - runs on server during dev, pre-rendered for static build if static middleware present
const serverLoader = createServerFn({
  method: "GET",
})
  .middleware([staticFunctionMiddleware])
  .inputValidator((slugs: string[]) => slugs)
  .handler(async ({ data: slugs }) => {
    const page = source.getPage(slugs);
    if (!page) throw notFound();
    const url = slugs.length > 0 ? `/docs/${slugs.join("/")}` : "/docs";
    return {
      pageTree: await source.serializePageTree(source.getPageTree()),
      path: page.path,
      url,
      title: page.data.title as string,
      description: (page.data.description as string) ?? "",
    };
  });

export const Route = createFileRoute("/docs/$")({
  component: Page,
  loader: async ({ params }): Promise<DocsPageLoaderData> => {
    const raw = params._splat;
    const slugs = raw && raw.length > 0 ? raw.split("/") : [];
    const data = await serverLoader({ data: slugs });
    await clientLoader.preload(data.path);
    return data;
  },
  head: ({ loaderData }) => ({
    meta: loaderData
      ? seo({
          title: loaderData.title,
          description: loaderData.description,
          path: loaderData.url,
        })
      : [],
    links: loaderData ? [canonicalLink(loaderData.url)] : [],
  }),
});

function renderDescription(description: string) {
  if (!description.includes(DIDS_LABEL)) return description;

  const [before, after] = description.split(DIDS_LABEL);

  return (
    <>
      {before}
      <Link
        to="/docs/$"
        params={{ _splat: DIDS_DOCS_SLUG }}
        className="font-medium underline underline-offset-4"
      >
        <span>{DIDS_LABEL}</span>
      </Link>
      {after}
    </>
  );
}

const clientLoader = browserCollections.docs.createClientLoader<Record<string, never>>({
  id: "docs",
  component({ toc, frontmatter, default: MDX }) {
    const description =
      typeof frontmatter.description === "string" ? frontmatter.description : "";
    const hideDescription =
      "hideDescription" in frontmatter &&
      (frontmatter as Record<string, unknown>).hideDescription === true;

    return (
      <DocsPage toc={toc}>
        <DocsTitle>{frontmatter.title}</DocsTitle>
        {!hideDescription && description ? (
          <DocsDescription>{renderDescription(description)}</DocsDescription>
        ) : null}
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
