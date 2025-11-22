import { useQuery, queryOptions } from "@tanstack/react-query";
import { fetchProvidersApi } from "@/lib/api/repository-provider-api";
import { getProviderDisplayName } from "@/lib/utils/provider-utils";
import type { Provider } from "@/types/repository-provider";

/**
 * Query options factory for repository providers
 * Can be used in both hooks and route loaders for consistent caching
 *
 * @returns TanStack Query options object
 *
 * @example
 * ```tsx
 * // In a route loader
 * loader: ({ context }) => context.queryClient.ensureQueryData(providersQueryOptions())
 *
 * // In a component
 * const { data: providers } = useProviderData();
 * ```
 */
export function providersQueryOptions() {
  return queryOptions({
    queryKey: ["repository-providers"],
    queryFn: async (): Promise<Provider[]> => {
      const providerKeys = await fetchProvidersApi();
      return providerKeys.map((key) => ({
        provider_key: key,
        display_name: getProviderDisplayName(key),
      }));
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });
}

/**
 * Hook to fetch and manage repository provider data using TanStack Query
 *
 * Replaces the manual Zustand store pattern with automatic caching,
 * loading states, and error handling from React Query.
 *
 * @returns Query result with provider data, loading and error states
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { data: providers, isPending, isError, error } = useProviderData();
 *
 *   if (isPending) return <div>Loading providers...</div>;
 *   if (isError) return <div>Error: {error.message}</div>;
 *
 *   return (
 *     <ul>
 *       {providers?.map(p => <li key={p.provider_key}>{p.display_name}</li>)}
 *     </ul>
 *   );
 * }
 * ```
 */
export function useProviderData() {
  return useQuery(providersQueryOptions());
}
