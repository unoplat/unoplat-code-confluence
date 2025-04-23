import React, { useEffect } from 'react';
import { createFileRoute, Outlet, useNavigate, useRouterState } from '@tanstack/react-router';

export const Route = createFileRoute('/_app')({
  component: AppComponent,
});

function AppComponent(): React.ReactElement {
  const navigate = useNavigate();
  const routerState = useRouterState();

  // Handle root path navigation
  useEffect(() => {
    if (routerState.location.pathname === '/') {
      navigate({ to: '/onboarding' });
    }
  }, [navigate, routerState.location.pathname]);

  return (
    <>
      <Outlet />
    </>
  );
}