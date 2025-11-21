import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { RepositoryProviderForm } from "@/components/custom/RepositoryProviderForm";
import { useProviderStore } from "@/stores/providerStore";
import { ProviderTabNavigation } from "@/components/custom/ProviderTabNavigation";

export default function OnboardingPage(): React.ReactElement {
  const providers = useProviderStore((state) => state.providers);

  if (!providers.length) {
    return (
      <div className="container mx-auto max-w-4xl px-4 py-12">
        <Card>
          <CardHeader className="text-center">
            <CardTitle>Connect a repository provider</CardTitle>
            <CardDescription>
              Add GitHub or GitHub Enterprise to start browsing repositories.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <RepositoryProviderForm inline />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-7xl space-y-6 px-4 py-8">
      <ProviderTabNavigation />
    </div>
  );
}
