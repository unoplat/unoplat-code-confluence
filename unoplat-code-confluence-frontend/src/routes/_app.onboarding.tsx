import React from "react";
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { ProviderTabNavigation } from "@/components/custom/ProviderTabNavigation";
import {
  providersQueryOptions,
  useProviderData,
} from "@/hooks/use-provider-data";
import { getProviderRouteSlug } from "@/lib/utils/provider-route-utils";

export const Route = createFileRoute("/_app/onboarding")({
  loader: async ({ context }) => {
    // Prefetch providers into TanStack Query cache
    const providers = await context.queryClient.ensureQueryData(
      providersQueryOptions(),
    );
    return { providers };
  },
  beforeLoad: async ({ context, location }) => {
    // Fetch providers to check if redirect is needed
    const providers = await context.queryClient.ensureQueryData(
      providersQueryOptions(),
    );

    // Treat /onboarding and /onboarding/ as index so we can redirect to first provider
    const isIndexPath =
      location.pathname === "/onboarding" ||
      location.pathname === "/onboarding/";

    // Redirect to first provider if providers exist and we're on the index
    if (providers && providers.length > 0 && isIndexPath) {
      const firstProvider = providers[0];
      const routeSlug = getProviderRouteSlug(firstProvider.provider_key);

      if (routeSlug) {
        throw redirect({
          to: "/onboarding/$provider",
          params: { provider: routeSlug },
          replace: true,
        });
      }
    }

    return { getTitle: () => "Onboarding" };
  },
  component: OnboardingLayout,
});

function OnboardingLayout(): React.ReactElement {
  const {
    data: providers,
    isPending,
    isError,
    error,
    refetch,
  } = useProviderData();

  if (isPending) {
    return (
      <div className="container mx-auto max-w-4xl px-4 py-12">
        <div className="space-y-3">
          <div className="bg-muted h-9 w-48 animate-pulse rounded-md" />
          <div className="h-32 animate-pulse rounded-md border border-dashed" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto max-w-4xl px-4 py-12">
        <div className="space-y-4 rounded-lg border border-dashed p-8 text-center">
          <p className="text-destructive text-sm">
            {error?.message || "Failed to load providers"}
          </p>
          <button
            type="button"
            className="text-primary text-sm font-medium underline-offset-4 hover:underline"
            onClick={() => void refetch()}
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (!providers || providers.length === 0) {
    return (
      <div className="container mx-auto max-w-7xl px-4 py-8">
        <Outlet />
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-7xl space-y-6 px-4 py-8">
      <ProviderTabNavigation />
      <Outlet />
    </div>
  );
}
