import 'wicg-inert';
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider, createRouter } from '@tanstack/react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// Import the generated route tree
import { routeTree } from './routeTree.gen'
import { ThemeProvider } from '@/components/custom/ThemeProvider'

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
})

// Create a router instance
const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
  // Add the query client to context
  context: {
    queryClient,
  },
})

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

/*
Rendering with createRoot:
Using createRoot from react-dom/client is the modern way to attach your
React application to a DOM element (here, an element with the ID "root"). 
This is the entry point where your app is bootstrapped.
*/
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <RouterProvider router={router} />
        {/* <ReactQueryDevtools initialIsOpen={true} /> */}
      </ThemeProvider>
    </QueryClientProvider>
    
  </StrictMode>,
)

// Initialize stagewise toolbar in development mode only
// TEMPORARILY DISABLED to debug sidebar header issue
// if (process.env.NODE_ENV === 'development') {
//   const stagewiseConfig = {
//     plugins: []
//   };

//   // Create a separate React root for the stagewise toolbar
//   const stagewiseContainer = document.createElement('div');
//   stagewiseContainer.id = 'stagewise-toolbar-container';
//   document.body.appendChild(stagewiseContainer);
  
//   createRoot(stagewiseContainer).render(
//     <StagewiseToolbar config={stagewiseConfig} />
//   );
// }
