import React from 'react';
import { Outlet, useRouterState, Link } from '@tanstack/react-router';
import { Toaster } from '../ui/toaster';
import { SidebarInset,SidebarProvider, SidebarTrigger } from '../ui/sidebar';
import { AppSidebar } from '@/components/custom/AppSidebar';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '../ui/breadcrumb'
import { Separator } from '@/components/ui/separator'

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
 * - Clicking "GitHub Onboarding" (to "/onboarding") and "Ingestion Dashboard"
 *   (to "/dashboard") renders components from `_app.onboarding.tsx` and `_app.dashboard.tsx`
 *   respectively in the <Outlet />.
 * 
 * The <Outlet /> plays a critical role as it acts as a placeholder. When a user navigates,
 * TanStack Router replaces the content inside the <Outlet /> with the corresponding matched route,
 * while keeping the rest of the Layout (like the header) intact.
 */

// Type guard for context with getTitle
function hasGetTitle(context: unknown): context is { getTitle: () => string } {
  return (
    typeof context === 'object' &&
    context !== null &&
    typeof (context as { getTitle?: unknown }).getTitle === 'function'
  );
}

export function Layout(): React.ReactElement {
  const matches = useRouterState({ select: (s) => s.matches });

  // Only include matches with a getTitle function in their context
  const crumbs = matches
    .filter((match) => hasGetTitle(match.context))
    .map(({ pathname, context }, idx, arr) => ({
      title: context.getTitle(),
      path: pathname,
      isLast: idx === arr.length - 1,
    }));

  // Deduplicate by title+path (in case of double-matches)
  const breadcrumbs = crumbs.filter(
    (crumb, idx, arr) =>
      arr.findIndex(
        (c) => c.title === crumb.title && c.path === crumb.path
      ) === idx
  );

  return (
      <div className="flex flex-col h-screen">
        <SidebarProvider>
          <div className="flex flex-1 bg-muted/30">
            <AppSidebar />
            <SidebarInset>
              <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
                <div className="flex items-center gap-2 px-4">
                  <SidebarTrigger className="-ml-1" />
                  <Separator orientation="vertical" className="mr-2 h-4" />
                  <Breadcrumb>
                    <BreadcrumbList>
                      {breadcrumbs.map((crumb) => (
                        <React.Fragment key={crumb.path}>
                          <BreadcrumbItem>
                            {crumb.isLast ? (
                              <BreadcrumbPage>{crumb.title}</BreadcrumbPage>
                            ) : (
                              <Link to={crumb.path}>{crumb.title}</Link>
                            )}
                          </BreadcrumbItem>
                          {!crumb.isLast && (
                            <BreadcrumbSeparator className="hidden md:block" />
                          )}
                        </React.Fragment>
                      ))}
                    </BreadcrumbList>
                  </Breadcrumb>
                </div>
              </header>
              <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
                <Outlet />
              </div>
            </SidebarInset>
          </div>
        </SidebarProvider>
        <Toaster />
      </div>
  );
}
