import React from 'react'
import { createRootRoute, redirect } from '@tanstack/react-router'
import { Layout } from '../components/custom/Layout'

// Import the styles
import '../styles/app.css'

// Custom NotFound component
// This will be displayed whenever a user navigates to a route that doesn't exist
// It serves as a fallback UI when no routes match the current URL
function NotFoundComponent(): React.ReactElement {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-foreground">404</h1>
        <p className="text-xl mt-2 text-muted-foreground">Page Not Found</p>
        <p className="mt-4 text-muted-foreground">The page you're looking for doesn't exist or has been moved.</p>
      </div>
    </div>
  )
}

// Root Route Declaration
// This is the foundation of the entire routing hierarchy and is ALWAYS rendered
// regardless of which route the user is currently viewing
// 
// The root route:
// 1. Is always the first component rendered in the route tree
// 2. Serves as a wrapper for all other routes
// 3. Provides a place to put UI elements that should appear on every page
// 4. Can define the notFoundComponent that renders when no routes match
export const Route = createRootRoute({
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  beforeLoad: ({ location }) => {
    // Redirect from / to /onboarding
    if (location.pathname === '/') {
      throw redirect({ to: '/onboarding', replace: true });
    }
    // No title needed from root as Layout adds Home icon
    return {}; // Return empty object or context without getTitle
  },
})

// The main component rendered by the root route
// This is the entry point for all routes in the application
// It renders the Layout component which contains the primary UI structure
// including navigation and the <Outlet /> where child routes will render
function RootComponent(): React.ReactElement {
  return <Layout />
}
    

    
  
