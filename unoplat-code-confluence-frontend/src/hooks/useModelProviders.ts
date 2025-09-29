import { useQuery } from '@tanstack/react-query';
import { getModelProviders } from '@/lib/api';

/**
 * TanStack Query hook for fetching model providers from the query engine
 * The API already transforms the backend record format to an array with backfilled provider_key
 *
 * @returns Query result with provider definitions array and loading/error states
 */
export const useModelProviders = () => {
  return useQuery({
    queryKey: ['model-providers'],
    queryFn: getModelProviders,
    staleTime: 5 * 60 * 1000, // 5 minutes - providers don't change often
    gcTime: 10 * 60 * 1000, // 10 minutes garbage collection time
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

/**
 * Hook to get a specific provider by key
 * Searches through the providers array to find a matching provider
 *
 * @param providerKey - The provider key to look up
 * @returns The provider definition or undefined if not found
 */
export const useModelProvider = (providerKey: string | undefined) => {
  const { data, ...rest } = useModelProviders();

  return {
    ...rest,
    data: providerKey && data
      ? data.find(provider => provider.provider_key === providerKey)
      : undefined,
  };
};