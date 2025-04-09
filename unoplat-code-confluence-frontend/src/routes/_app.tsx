import React, { useState, useEffect } from 'react';
import { createFileRoute, Outlet, useNavigate, useRouterState } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import GitHubTokenPopup from '../components/GitHubTokenPopup';
import { getFlagStatus } from '../lib/api';
import { FlagResponse } from '../types';

export const Route = createFileRoute('/_app')({
  component: AppComponent,
});

function AppComponent(): React.ReactElement {
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  const navigate = useNavigate();
  const routerState = useRouterState();
  
  // Query for token submission status
  const { data: tokenStatus } = useQuery<FlagResponse>({
    queryKey: ['flags', 'isTokenSubmitted'],
    queryFn: () => getFlagStatus('isTokenSubmitted'),
  });

  // Show token popup if no token is present
  useEffect(() => {
    if (tokenStatus && !tokenStatus.status) {
      setShowTokenPopup(true);
    }
  }, [tokenStatus]);

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
        onClose={() => setShowTokenPopup(false)} 
      />
      <Outlet />
    </>
  );
}