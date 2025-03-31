import React, { useState } from 'react';
import { Link, Outlet } from '@tanstack/react-router';
import { Button } from './ui/button';
import { cn } from '@/lib/utils';
import { LayoutDashboard, FileCode, Settings } from 'lucide-react';
import { Toaster } from './ui/toaster';

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
export function Layout(): React.ReactElement {
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);

  const toggleSidebar = (): void => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="flex h-screen bg-muted/30">
      {/* Sidebar Navigation */}
      <div 
        className={cn(
          "bg-card border-r border-border",
          sidebarCollapsed ? "w-16" : "w-64",
          "transition-all duration-300 ease-in-out z-10"
        )}
      >
        {/* App Title/Logo Section */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          {!sidebarCollapsed && (
            <h1 className="text-xl font-bold text-foreground">
              Unoplat Code Confluence
            </h1>
          )}
          {/* Toggle Button */}
          <Button 
            onClick={toggleSidebar}
            variant="ghost"
            size="icon"
            aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-muted-foreground"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                d={sidebarCollapsed 
                  ? "M9 5l7 7-7 7" 
                  : "M15 19l-7-7 7-7"
                } 
              />
            </svg>
          </Button>
        </div>
        
        {/* Navigation Links */}
        <nav className="px-2 py-6 space-y-1">
          <Link
            to="/onboarding"
            className={cn(
              "flex items-center px-3 py-2.5 text-sm font-medium rounded-md",
              "hover:bg-muted/70 transition-colors",
              sidebarCollapsed ? "justify-center" : "",
              "text-foreground"
            )}
            activeProps={{
              className: cn(
                "flex items-center px-3 py-2.5 text-sm font-medium rounded-md",
                "bg-muted text-primary",
                sidebarCollapsed ? "justify-center" : ""
              ),
            }}
          >
            <FileCode className={cn("h-5 w-5", sidebarCollapsed ? '' : 'mr-3')} />
            {!sidebarCollapsed && 'GitHub Onboarding'}
          </Link>
          
          <a
            href="http://localhost:8080/namespaces/default/workflows"
            className={cn(
              "flex items-center px-3 py-2.5 text-sm font-medium rounded-md",
              "hover:bg-muted/70 transition-colors",
              sidebarCollapsed ? "justify-center" : "",
              "text-foreground"
            )}
          >
            <LayoutDashboard className={cn("h-5 w-5", sidebarCollapsed ? '' : 'mr-3')} />
            {!sidebarCollapsed && 'Ingestion Dashboard'}
          </a>

          <Link
            to="/settings"
            className={cn(
              "flex items-center px-3 py-2.5 text-sm font-medium rounded-md",
              "hover:bg-muted/70 transition-colors",
              sidebarCollapsed ? "justify-center" : "",
              "text-foreground"
            )}
            activeProps={{
              className: cn(
                "flex items-center px-3 py-2.5 text-sm font-medium rounded-md",
                "bg-muted text-primary",
                sidebarCollapsed ? "justify-center" : ""
              ),
            }}
          >
            <Settings className={cn("h-5 w-5", sidebarCollapsed ? '' : 'mr-3')} />
            {!sidebarCollapsed && 'Settings'}
          </Link>
        </nav>
      </div>
      
      {/* Main Content Area */}
      <div className="flex-1 overflow-auto">
        <main className="p-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
      
      {/* Toast Notifications */}
      <Toaster />
    </div>
  );
}