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

export const Route = createFileRoute("/_app/onboarding/github")({
  beforeLoad: () => {
    // Select the GitHub provider when this route is accessed
    useProviderStore.getState().selectProvider(ProviderKey.GITHUB_OPEN);
    return { getTitle: () => "Onboarding" };
  },
  component: GitHubOnboardingRoute,
});

function GitHubOnboardingRoute(): React.ReactElement {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>GitHub Repositories</CardTitle>
          <CardDescription>
            Connect your GitHub repositories to ingest them into Unoplat Code
            Confluence.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <RepositoryDataTable
            providerKey={ProviderKey.GITHUB_OPEN}
            tokenStatus
          />
        </CardContent>
      </Card>
    </div>
  );
}
