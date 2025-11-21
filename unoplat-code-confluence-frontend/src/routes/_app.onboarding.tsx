import React from "react";
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { ProviderTabNavigation } from "@/components/custom/ProviderTabNavigation";
import { useProviderStore } from "@/stores/providerStore";

export const Route = createFileRoute("/_app/onboarding")({
  beforeLoad: async ({ location }) => {
    const store = useProviderStore.getState();

    // Fetch providers if not already loaded
    if (store.providers.length === 0) {
      await store.fetchProviders();
    }

    const isIndexPath =
      location.pathname === "/onboarding" ||
      location.pathname === "/onboarding/";

    // Get updated providers after fetch
    const providers = useProviderStore.getState().providers;
    const firstProvider = providers[0];

    // Redirect to first provider if on index path
    if (firstProvider && isIndexPath) {
      throw redirect({
        to:
          firstProvider.provider_key === "github_enterprise"
            ? "/onboarding/github-enterprise"
            : "/onboarding/github",
        replace: true,
      });
    }

    return { getTitle: () => "Onboarding" };
  },
  component: OnboardingLayout,
});

function OnboardingLayout(): React.ReactElement {
  const providers = useProviderStore((s) => s.providers);
  const isLoading = useProviderStore((s) => s.isLoading);
  const error = useProviderStore((s) => s.error);
  const fetchProviders = useProviderStore((s) => s.fetchProviders);

  if (isLoading) {
    return (
      <div className="container mx-auto max-w-4xl px-4 py-12">
        <div className="space-y-3">
          <div className="bg-muted h-9 w-48 animate-pulse rounded-md" />
          <div className="h-32 animate-pulse rounded-md border border-dashed" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto max-w-4xl px-4 py-12">
        <div className="space-y-4 rounded-lg border border-dashed p-8 text-center">
          <p className="text-destructive text-sm">{error}</p>
          <button
            type="button"
            className="text-primary text-sm font-medium underline-offset-4 hover:underline"
            onClick={() => void fetchProviders()}
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (!providers.length) {
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
