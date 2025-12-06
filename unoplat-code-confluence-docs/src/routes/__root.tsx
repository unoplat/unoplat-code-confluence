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
        <HeadContent />
      </head>
      <body className="flex flex-col min-h-screen">
        <RootProvider components={{ Link: CustomLink }}>{children}</RootProvider>
        <Scripts />
      </body>
    </html>
  );
}
