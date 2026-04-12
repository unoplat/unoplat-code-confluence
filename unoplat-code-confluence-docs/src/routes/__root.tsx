import {
  createRootRoute,
  HeadContent,
  Link,
  Outlet,
  Scripts,
} from "@tanstack/react-router";
import * as React from "react";
import { forwardRef } from "react";
import appCss from "@/styles/app.css?url";
import { RootProvider } from "fumadocs-ui/provider/tanstack";
import { Banner } from "fumadocs-ui/components/banner";
import DefaultSearchDialog from "@/components/search-dialog";
import { bannerConfig } from "@/lib/banner-config";
import {
  seo,
  DEFAULT_DESCRIPTION,
  SITE_NAME,
  SITE_URL,
} from "@/lib/seo";

// Minimal skeleton CSS to prevent FOUC (Flash of Unstyled Content)
// Only html/body rules are kept — layout-specific rules (#nd-docs-layout, #nd-sidebar, etc.)
// are omitted to avoid ID-level specificity conflicts with Fumadocs hydrated styles.
const SKELETON_STYLES = `
html,body{margin:0;min-height:100%;font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,sans-serif}
body{display:flex;flex-direction:column;min-height:100vh}
@media(prefers-color-scheme:dark){html:not(.light),html:not(.light) body{background:hsl(0,0%,7.04%);color:hsl(0,0%,92%)}}
html.dark,html.dark body{background:hsl(0,0%,7.04%);color:hsl(0,0%,92%)}
`;

// Static file extensions that should bypass TanStack Router
const STATIC_FILE_PATTERN = /\.(json|pdf|zip|csv|xml|txt|png|jpg|jpeg|gif|svg|ico|webp)$/i;

interface CustomLinkProps {
  href?: string;
  prefetch?: boolean;
  children?: React.ReactNode;
  className?: string;
  target?: string;
  rel?: string;
}

// Custom Link component that handles static files with native <a> tags
// This prevents TanStack Router from intercepting clicks to static assets
const CustomLink = forwardRef<HTMLAnchorElement, CustomLinkProps>(
  function CustomLink({ href = "", prefetch = true, children, ...props }, ref) {
    // Use native <a> for static files to bypass router
    if (STATIC_FILE_PATTERN.test(href)) {
      return (
        <a ref={ref} href={href} {...props}>
          {children}
        </a>
      );
    }

<<<<<<< HEAD
    // Split hash fragment from href so TanStack Router receives it
    // via its dedicated `hash` prop instead of embedded in `to`
    const hashIndex = href.indexOf("#");
    const path = hashIndex >= 0 ? href.slice(0, hashIndex) : href;
    const hash = hashIndex >= 0 ? href.slice(hashIndex + 1) : undefined;

    // Use TanStack Router Link for route navigation
    return (
      <Link
        ref={ref}
        to={path || "."}
        hash={hash}
        preload={prefetch ? "intent" : false}
        {...props}
      >
=======
    // Use TanStack Router Link for route navigation
    return (
      <Link ref={ref} to={href} preload={prefetch ? "intent" : false} {...props}>
>>>>>>> origin/main
        {children}
      </Link>
    );
  }
);

export const Route = createRootRoute({
  head: () => ({
    meta: [
      {
        charSet: "utf-8",
      },
      {
        name: "viewport",
        content: "width=device-width, initial-scale=1",
      },
      ...seo({ title: SITE_NAME, description: DEFAULT_DESCRIPTION }),
    ],
    links: [{ rel: "stylesheet", href: appCss }],
    scripts: [
      {
        type: "application/ld+json",
        children: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "WebSite",
          name: SITE_NAME,
          url: SITE_URL,
          description: DEFAULT_DESCRIPTION,
        }),
      },
    ],
  }),
  component: RootComponent,
});

function RootComponent() {
  return (
    <RootDocument>
      <Outlet />
    </RootDocument>
  );
}

function RootDocument({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <style
          data-crit="docs-skeleton"
          dangerouslySetInnerHTML={{ __html: SKELETON_STYLES }}
        />
        <HeadContent />
      </head>
      <body className="flex flex-col min-h-screen">
        {bannerConfig.enabled && (
          <Banner id={bannerConfig.id} variant={bannerConfig.variant}>
            {bannerConfig.message}
            {bannerConfig.linkUrl && (
              <>
                {" "}
                <Link
                  to={bannerConfig.linkUrl}
                  className="font-medium underline underline-offset-4"
                >
                  {bannerConfig.linkText ?? "Learn more"}
                </Link>
              </>
            )}
          </Banner>
        )}
        <RootProvider
          components={{ Link: CustomLink }}
          search={{
            enabled: true,
            SearchDialog: DefaultSearchDialog,
          }}
        >
          {children}
        </RootProvider>
        <Scripts />
      </body>
    </html>
  );
}
