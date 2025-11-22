import React from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RepositoryDataTable } from "@/components/custom/RepositoryDataTable";
import { providersQueryOptions } from "@/hooks/use-provider-data";
import type { Provider } from "@/types/repository-provider";
import {
  getProviderFromSlug,
  getProviderMetadata,
} from "@/lib/utils/provider-route-utils";

export const Route = createFileRoute("/_app/onboarding/$provider")({
  loader: async (opts) => {
    const { params, context, location } = opts;
    console.debug("[ROUTER-DEBUG] Onboarding.$provider.loader.enter", {
      pathname: location.pathname,
      params,
    });
    // Fetch providers to validate the route param (warm cache)
    const providers: Provider[] = await context.queryClient.ensureQueryData(
      providersQueryOptions(),
    );

    // Convert route slug to provider key
    const providerKey = getProviderFromSlug(params.provider);

    // Validate: provider must be supported; if we already have providers cached,
    // ensure it exists. When the list is empty (fresh connect), allow it so
    // we don't bounce back before the list refetches.
    const exists = providers.some((p: Provider) => p.provider_key === providerKey);

    console.debug("[ROUTER-DEBUG] Onboarding.$provider.loader.providerCheck", {
      providerKey,
      exists,
      providerKeys: providers.map((p: Provider) => p.provider_key),
    });

    if (!providerKey) {
      console.debug(
        "[ROUTER-DEBUG] Onboarding.$provider.loader.redirect.invalidProviderKey -> /onboarding",
        { providerKey },
      );
      throw redirect({ to: "/onboarding", replace: true });
    }

    if (providers.length > 0 && !exists) {
      console.debug(
        "[ROUTER-DEBUG] Onboarding.$provider.loader.redirect.providerNotInCache -> /onboarding",
        { providerKey, providerKeys: providers.map((p: Provider) => p.provider_key) },
      );
      throw redirect({ to: "/onboarding", replace: true });
    }

    // Get metadata for this provider
    const metadata = getProviderMetadata(providerKey);

    if (!metadata) {
      console.debug(
        "[ROUTER-DEBUG] Onboarding.$provider.loader.redirect.missingMetadata -> /onboarding",
        { providerKey },
      );
      // Provider not supported yet (e.g., GitLab)
      throw redirect({ to: "/onboarding", replace: true });
    }

    console.debug("[ROUTER-DEBUG] Onboarding.$provider.loader.success", {
      providerKey,
      metadataTitle: metadata.title,
    });

    return { providerKey, metadata };
  },
  beforeLoad: ({ params, location }) => {
    console.debug("[ROUTER-DEBUG] Onboarding.$provider.beforeLoad.enter", {
      pathname: location.pathname,
      params,
    });
    const providerKey = getProviderFromSlug(params.provider);
    const metadata = providerKey ? getProviderMetadata(providerKey) : null;

    if (!providerKey || !metadata) {
      console.debug(
        "[ROUTER-DEBUG] Onboarding.$provider.beforeLoad.redirect.invalidProvider -> /onboarding",
        { providerKey, hasMetadata: !!metadata },
      );
      throw redirect({ to: "/onboarding", replace: true });
    }

    console.debug("[ROUTER-DEBUG] Onboarding.$provider.beforeLoad.getTitle", {
      title: metadata.title,
    });

    return { getTitle: () => metadata.title };
  },
  component: ProviderRoute,
});

function ProviderRoute(): React.ReactElement {
  const { providerKey, metadata } = Route.useLoaderData();

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{metadata.title}</CardTitle>
          <CardDescription>{metadata.description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <RepositoryDataTable providerKey={providerKey} tokenStatus />
        </CardContent>
      </Card>
    </div>
  );
}
