import { useQuery } from "@tanstack/react-query";
import { getModelConfig } from "@/lib/api";

/**
 * TanStack Query hook for fetching existing model configuration
 * Returns null if no configuration exists (404 from backend)
 *
 * @returns Query result with model configuration or null
 */
export const useModelConfig = () => {
  return useQuery({
    queryKey: ["model-config"],
    queryFn: getModelConfig,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes garbage collection time
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};