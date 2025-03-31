import React, { useState, useEffect } from 'react';
import { createFileRoute, Outlet, useNavigate, useRouterState } from '@tanstack/react-router';
import GitHubTokenPopup from '../components/GitHubTokenPopup';

export const Route = createFileRoute('/_app')({
  component: AppComponent,
});

function AppComponent(): React.ReactElement {
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  const navigate = useNavigate();
  const routerState = useRouterState();
  
  useEffect(() => {
    // Check if token has been submitted before
    const hasSubmittedToken = localStorage.getItem('hasSubmittedToken');
    if (!hasSubmittedToken) {
      setShowTokenPopup(true);
    }
    
    // If user is at root path '/', redirect to /onboarding
    if (routerState.location.pathname === '/') {
      navigate({ to: '/onboarding' });
    }
  }, [navigate, routerState.location.pathname]);
  
  return (
    <>
      <GitHubTokenPopup 
        open={showTokenPopup} 
        onClose={() => setShowTokenPopup(false)} 
      />
      <Outlet />
    </>
  );
}