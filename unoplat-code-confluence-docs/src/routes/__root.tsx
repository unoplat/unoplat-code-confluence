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
import DefaultSearchDialog from "@/components/search-dialog";

// Minimal skeleton CSS to prevent FOUC (Flash of Unstyled Content)
// Matches fumadocs 3-column grid layout with correct colors and dimensions
const SKELETON_STYLES = `
html,body{margin:0;min-height:100%;font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,sans-serif;background:hsl(0,0%,96%);color:hsl(0,0%,3.9%)}
body{display:flex;flex-direction:column;min-height:100vh}
#nd-docs-layout{display:grid;min-height:100dvh;grid-template:"sidebar header toc" "sidebar toc-popover toc" "sidebar main toc" 1fr/268px 1fr 268px}
#nd-sidebar{grid-area:sidebar;background:hsl(0,0%,94.7%);border-right:1px solid hsla(0,0%,80%,50%)}
#nd-page{grid-area:main;padding:56px 32px 24px;max-width:900px;margin:0 auto;line-height:1.6}
#nd-toc{grid-area:toc;padding-top:48px}
@media(max-width:1280px){#nd-docs-layout{grid-template-columns:268px 1fr 0}#nd-toc{display:none}}
@media(max-width:768px){#nd-docs-layout{grid-template-columns:0 1fr 0}#nd-sidebar{display:none}}
@media(prefers-color-scheme:dark){html:not(.light),html:not(.light) body{background:hsl(0,0%,7.04%);color:hsl(0,0%,92%)}html:not(.light) #nd-sidebar{background:hsl(0,0%,9.8%);border-right-color:hsla(0,0%,40%,20%)}}
html.dark,html.dark body{background:hsl(0,0%,7.04%);color:hsl(0,0%,92%)}
html.dark #nd-sidebar{background:hsl(0,0%,9.8%);border-right-color:hsla(0,0%,40%,20%)}
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

    // Use TanStack Router Link for route navigation
    return (
      <Link ref={ref} to={href} preload={prefetch ? "intent" : false} {...props}>
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
      {
        title: "Unoplat Code Confluence Docs",
      },
    ],
    links: [{ rel: "stylesheet", href: appCss }],
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
    <html suppressHydrationWarning>
      <head>
        <style
          data-crit="docs-skeleton"
          dangerouslySetInnerHTML={{ __html: SKELETON_STYLES }}
        />
        <HeadContent />
      </head>
      <body className="flex flex-col min-h-screen">
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
