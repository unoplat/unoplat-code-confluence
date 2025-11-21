import React from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RepositoryDataTable } from "@/components/custom/RepositoryDataTable";
import { ProviderKey } from "@/types/credential-enums";
import { useProviderStore } from "@/stores/providerStore";

export const Route = createFileRoute("/_app/onboarding/github-enterprise")({
  beforeLoad: () => {
    // Select the GitHub Enterprise provider when this route is accessed
    useProviderStore.getState().selectProvider(ProviderKey.GITHUB_ENTERPRISE);
    return { getTitle: () => "Onboarding" };
  },
  component: GitHubEnterpriseOnboardingRoute,
});

function GitHubEnterpriseOnboardingRoute(): React.ReactElement {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>GitHub Enterprise Repositories</CardTitle>
          <CardDescription>
            Connect a self-hosted GitHub Enterprise instance by supplying its
            URL and a PAT.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <RepositoryDataTable
            providerKey={ProviderKey.GITHUB_ENTERPRISE}
            tokenStatus
          />
        </CardContent>
      </Card>
    </div>
  );
}
