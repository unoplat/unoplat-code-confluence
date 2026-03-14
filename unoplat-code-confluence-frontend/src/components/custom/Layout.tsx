import React from "react";
import { Outlet, useRouterState, Link } from "@tanstack/react-router";
import { NuqsAdapter } from "nuqs/adapters/tanstack-router";
import { Toaster } from "../ui/sonner";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "../ui/sidebar";
import { AppSidebar } from "@/components/custom/AppSidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "../ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Home, Github, BookOpen, Heart } from "lucide-react";
import indiaIcon from "@/assets/india-icon.png";
import { ModeToggle } from "./ModeToggle";
import { CommandPalette } from "@/components/custom/CommandPalette";
import { AppFeedbackSheet } from "@/features/app-feedback";
import { useCommandPaletteStore } from "@/stores/useCommandPaletteStore";
import { useAuthData } from "@/hooks/use-auth-data";

/**
 * Layout Component - Main Application Shell with Sidebar Navigation
 *
 * This component provides the consistent UI structure for the entire application.
 * It is rendered by the RootComponent from __root.tsx, and wraps all nested route content.
 *
 * Key responsibilities:
 * 1. Displays a persistent sidebar containing application title and navigation links.
 * 2. Uses TanStack Router's <Link> components for client-side navigation.
 * 3. Provides an <Outlet /> where the matched child route components are rendered.
 * 4. Initializes authentication state on application load.
 *
 * Navigation Flow:
 * - Clicking "Onboarding" (to "/onboarding") and "Ingestion Dashboard"
 *   (to "/dashboard") renders components from `_app.onboarding.tsx` and `_app.dashboard.tsx`
 *   respectively in the <Outlet />.
 *
 * The <Outlet /> plays a critical role as it acts as a placeholder. When a user navigates,
 * TanStack Router replaces the content inside the <Outlet /> with the corresponding matched route,
 * while keeping the rest of the Layout (like the header) intact.
 */

// Map category titles to their base paths
const categoryMap: Record<string, string[]> = {
  Workspace: ["/onboarding", "/operationsManagement", "/repositoryOperations"],
  Settings: ["/settings"],
};

// Type guard for context with getTitle
function hasGetTitle(context: unknown): context is { getTitle: () => string } {
  return (
    typeof context === "object" &&
    context !== null &&
    typeof (context as { getTitle?: unknown }).getTitle === "function"
  );
}

export function Layout(): React.ReactElement {
  // Initialize auth data (token status and user details) for the entire app
  useAuthData();
  const { open: openCommandPalette } = useCommandPaletteStore();

  const { matches, pathname } = useRouterState({
    select: (s) => ({ matches: s.matches, pathname: s.location.pathname }),
  });

  // Only include matches with a getTitle function in their context
  const crumbs = matches
    .filter((match) => hasGetTitle(match.context))
    .map(({ pathname: matchPathname, context }, idx, arr) => ({
      title: (context as { getTitle: () => string }).getTitle(),
      path: matchPathname,
      isLast: idx === arr.length - 1,
    }));

  // Debug logs

  console.log("Layout crumbs:", crumbs);

  // Deduplicate by title+path (in case of double-matches)
  const breadcrumbs = crumbs.filter(
    (crumb, idx, arr) =>
      arr.findIndex((c) => c.title === crumb.title && c.path === crumb.path) ===
      idx,
  );

  // Find the category for the current path
  let currentCategory: string | null = null;
  for (const category in categoryMap) {
    if (
      categoryMap[category].some((basePath) => pathname.startsWith(basePath))
    ) {
      currentCategory = category;
      break;
    }
  }

  return (
    <div className="flex h-screen flex-col">
      <SidebarProvider>
        <div className="bg-muted/30 flex flex-1">
          <AppSidebar />
          <SidebarInset>
            <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
              <div className="flex w-full items-center justify-between px-4">
                <div className="flex items-center gap-2">
                  <SidebarTrigger className="-ml-1" />
                  <Separator orientation="vertical" className="mr-2 h-4" />
                  <Breadcrumb>
                    <BreadcrumbList>
                      <BreadcrumbItem>
                        <Link
                          to="/"
                          className="text-sidebar-foreground hover:text-sidebar-accent-foreground inline-flex items-center align-middle text-sm font-medium"
                        >
                          <Home size={18} aria-label="Home" />
                        </Link>
                      </BreadcrumbItem>
                      {/* Render category crumb if exists */}
                      {currentCategory && (
                        <>
                          <BreadcrumbSeparator className="hidden md:block" />
                          <BreadcrumbItem>
                            <BreadcrumbPage className="text-sm font-medium">
                              {currentCategory}
                            </BreadcrumbPage>
                          </BreadcrumbItem>
                        </>
                      )}
                      {/* Render route crumbs */}
                      {breadcrumbs.length > 0 && !currentCategory && (
                        <BreadcrumbSeparator className="hidden md:block" />
                      )}
                      {breadcrumbs.map((crumb) => (
                        <React.Fragment key={crumb.path}>
                          <BreadcrumbSeparator className="hidden md:block" />
                          <BreadcrumbItem>
                            {crumb.isLast ? (
                              <BreadcrumbPage className="text-sm font-medium">
                                {crumb.title}
                              </BreadcrumbPage>
                            ) : (
                              <Link
                                to={crumb.path}
                                className="text-sidebar-foreground/80 hover:text-sidebar-foreground text-sm font-medium"
                              >
                                {crumb.title}
                              </Link>
                            )}
                          </BreadcrumbItem>
                        </React.Fragment>
                      ))}
                    </BreadcrumbList>
                  </Breadcrumb>
                </div>
                <div className="flex items-center space-x-4">
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-muted-foreground hidden gap-2 text-xs md:flex"
                    onClick={openCommandPalette}
                  >
                    <span>Search...</span>
                    <kbd className="bg-muted pointer-events-none inline-flex h-5 items-center gap-1 rounded border px-1.5 font-mono text-[10px] font-medium opacity-100 select-none">
                      <span className="text-xs">⌘</span>K
                    </kbd>
                  </Button>
                  <a
                    href="https://github.com/unoplat/unoplat-code-confluence"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-primary inline-flex items-center gap-2 text-sm font-medium transition-colors"
                  >
                    <Github size={18} />
                    <span>GitHub</span>
                  </a>
                  <a
                    href="https://docs.unoplat.io"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-primary inline-flex items-center gap-2 text-sm font-medium transition-colors"
                  >
                    <BookOpen size={18} />
                    <span>Docs</span>
                  </a>
                  <ModeToggle />
                </div>
              </div>
            </header>
            <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
              <NuqsAdapter>
                <Outlet />
              </NuqsAdapter>
            </div>
            <Separator className="bg-transparent" />
            <footer className="flex shrink-0 items-center justify-center gap-1.5 px-4 py-3">
              <span className="text-muted-foreground font-serif text-sm tracking-wide">
                Made with
              </span>
              <Heart
                size={14}
                className="fill-red-500 text-red-500"
                aria-label="love"
              />
              <span className="text-muted-foreground font-serif text-sm tracking-wide">
                from India
              </span>
              <img src={indiaIcon} alt="India" className="h-4 w-auto" />
            </footer>
          </SidebarInset>
        </div>
      </SidebarProvider>
      <CommandPalette />
      <AppFeedbackSheet />
      <Toaster />
    </div>
  );
}
