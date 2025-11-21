import React from "react";
import { Plus } from "lucide-react";
import { RepositoryProviderForm } from "./RepositoryProviderForm";
import { useProviderStore } from "@/stores/providerStore";
import { ProviderKey } from "@/types/credential-enums";

export function AddProviderButton(): React.ReactElement | null {
  const providers = useProviderStore((s) => s.providers);
  const hasEnterprise = providers.some(
    (p) => p.provider_key === ProviderKey.GITHUB_ENTERPRISE,
  );

  if (hasEnterprise) {
    return null;
  }

  return (
    <RepositoryProviderForm
      trigger={
        <button
          type="button"
          className="border-border text-muted-foreground hover:bg-muted flex h-9 w-9 items-center justify-center rounded-full border transition"
        >
          <Plus className="h-4 w-4" />
        </button>
      }
    />
  );
}
