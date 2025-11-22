// hooks/useAuthData.ts
import { useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchGitHubUser } from "@/lib/api";
import { useAuthStore } from "@/stores/useAuthStore";
import { ProviderKey } from "@/types/credential-enums";
import { providersQueryOptions } from "@/hooks/use-provider-data";

export const useAuthData = () => {
  const { setUser } = useAuthStore();

  // Load configured providers; enables user fetch when at least one exists.
  const providersQuery = useQuery(providersQueryOptions());

  // Prefer GitHub Open if present; otherwise fall back to first provider.
  const activeProviderKey = useMemo<ProviderKey | undefined>(() => {
    const providers = providersQuery.data;
    if (!providers || providers.length === 0) return undefined;

    const providerKeys = providers.map((p) => p.provider_key);

    if (providerKeys.includes(ProviderKey.GITHUB_OPEN)) {
      return ProviderKey.GITHUB_OPEN;
    }

    return providerKeys[0];
  }, [providersQuery.data]);

  // Fetch user once provider exists.
  const userQuery = useQuery({
    queryKey: ["githubUser", activeProviderKey],
    queryFn: () => fetchGitHubUser(activeProviderKey as ProviderKey),
    enabled: !!activeProviderKey,
  });

  useEffect(() => {
    if (userQuery.data) setUser(userQuery.data);
  }, [userQuery.data, setUser]);

  return { providersQuery, userQuery, activeProviderKey };
};
