import type { ProviderKey } from "@/types/credential-enums";
import type { GitHubRepoSummary, PaginatedResponse } from "@/types";
import { apiClient } from "./clients";

interface FetchReposParams {
  providerKey: ProviderKey;
  perPage: number;
  cursor?: string | null;
  nameFilter?: string;
}

/**
 * Fetch repositories from the backend for a given provider
 *
 * @param params - Fetch parameters including provider key, pagination, and filters
 * @returns Promise with paginated repository data
 */
export async function fetchRepositoriesApi({
  providerKey,
  perPage,
  cursor,
  nameFilter,
}: FetchReposParams): Promise<PaginatedResponse<GitHubRepoSummary>> {
  const filterValues =
    nameFilter && nameFilter.trim().length
      ? JSON.stringify({ name: nameFilter.trim() })
      : undefined;

  const { data } = await apiClient.get<PaginatedResponse<GitHubRepoSummary>>(
    "/repos",
    {
      params: {
        provider_key: providerKey,
        per_page: perPage,
        cursor: cursor ?? undefined,
        filterValues,
      },
    },
  );

  return data;
}
