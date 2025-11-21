import React from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { cn } from "@/lib/utils";
import {
  getProviderDisplayName,
  getProviderIcon,
} from "@/lib/utils/provider-utils";
import { useProviderStore } from "@/stores/providerStore";
import { AddProviderButton } from "./AddProviderButton";

export function ProviderTabNavigation(): React.ReactElement {
  const routerState = useRouterState();
  const activePath = routerState.location.pathname;
  const providers = useProviderStore((s) => s.providers);

  if (!providers.length) {
    return <AddProviderButton />;
  }

  const activeId =
    providers.find((tab) =>
      activePath.includes(tab.provider_key.replace("_", "-")),
    )?.provider_key ?? providers[0]?.provider_key;

  return (
    <div className="border-border border-b">
      <div className="flex flex-wrap items-center gap-2">
        {providers.map((provider) => {
          const Icon = getProviderIcon(provider.provider_key);
          const isActive = provider.provider_key === activeId;

          return (
            <Link
              key={provider.provider_key}
              to={
                provider.provider_key === "github_enterprise"
                  ? "/onboarding/github-enterprise"
                  : "/onboarding/github"
              }
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
