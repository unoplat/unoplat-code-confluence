import React, { useState, useEffect } from 'react';
import { createFileRoute, Outlet, useNavigate, useRouterState } from '@tanstack/react-router';
import GitHubTokenPopup from '../components/custom/GitHubTokenPopup';
import { useAuthStore } from '../stores/useAuthStore';
import { useAuthData } from '@/hooks/use-auth-data';

export const Route = createFileRoute('/_app')({
  component: AppComponent,
});

function AppComponent(): React.ReactElement {
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  const navigate = useNavigate();
  const routerState = useRouterState();
  
  // Use useAuthData hook which manages both querying and updating the Zustand store
  const { tokenQuery } = useAuthData();
  
  // Get tokenStatus from the store (which is updated by useAuthData)
  const tokenStatus = useAuthStore(state => state.tokenStatus);

  // Show token popup if no token is present
  useEffect(() => {
    // Skip the global popup when on the onboarding page (handled locally in OnboardingPage)
    if (routerState.location.pathname === '/onboarding') {
      setShowTokenPopup(false);
      return;
    }
    if (tokenStatus && !tokenStatus.status && tokenStatus.errorCode !== 503) {
      setShowTokenPopup(true);
    } else {
      setShowTokenPopup(false);
    }
  }, [tokenStatus, routerState.location.pathname]);

  // Handle root path navigation
  useEffect(() => {
    if (routerState.location.pathname === '/') {
      navigate({ to: '/onboarding' });
    }
  }, [navigate, routerState.location.pathname]);
  
  return (
    <>
      <GitHubTokenPopup 
        open={showTokenPopup} 
        onClose={() => {
          setShowTokenPopup(false);
          // Refresh token status query when popup is closed
          tokenQuery.refetch();
        }} 
      />
      <Outlet />
    </>
  );
}