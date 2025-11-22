import React from "react";
import { Link, useParams } from "@tanstack/react-router";
import { cn } from "@/lib/utils";
import {
  getProviderDisplayName,
  getProviderIcon,
} from "@/lib/utils/provider-utils";
import { getProviderRouteSlug } from "@/lib/utils/provider-route-utils";
import { useProviderData } from "@/hooks/use-provider-data";
import { AddProviderButton } from "./AddProviderButton";

export function ProviderTabNavigation(): React.ReactElement {
  const params = useParams({ strict: false });
  const { data: providers, isPending } = useProviderData();

  if (isPending) {
    return (
      <div className="border-border border-b">
        <div className="flex gap-2">
          <div className="bg-muted h-10 w-32 animate-pulse rounded-t-md" />
          <div className="bg-muted h-10 w-32 animate-pulse rounded-t-md" />
        </div>
      </div>
    );
  }

  if (!providers || providers.length === 0) {
    return <AddProviderButton />;
  }

  return (
    <div className="border-border border-b">
      <div className="flex flex-wrap items-center gap-2">
        {providers.map((provider) => {
          const Icon = getProviderIcon(provider.provider_key);
          const routeSlug = getProviderRouteSlug(provider.provider_key);

          // Skip providers without route support (e.g., GitLab not yet implemented)
          if (!routeSlug) return null;

          const isActive = params?.provider === routeSlug;

          return (
            // eslint-disable-next-line jsx-a11y/anchor-is-valid
            <Link
              key={provider.provider_key}
              to="/onboarding/$provider"
              params={{ provider: routeSlug }}
              preload="intent"
              className={cn(
                "flex items-center gap-2 rounded-t-md px-4 py-2 text-sm transition-colors",
                isActive
                  ? "bg-background border-border border-b-background border font-semibold"
                  : "text-muted-foreground hover:text-foreground border border-transparent",
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{getProviderDisplayName(provider.provider_key)}</span>
            </Link>
          );
        })}
        <AddProviderButton />
      </div>
    </div>
  );
}
