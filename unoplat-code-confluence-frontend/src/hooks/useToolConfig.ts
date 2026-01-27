import { useQuery } from "@tanstack/react-query";
import { getToolConfig, getToolConfigs } from "@/lib/api/tool-config-api";
import type { ToolProvider } from "@/features/tool-config/types";

/**
 * TanStack Query hook for fetching all tool configurations
 * @returns Query result with list of tool configurations
 */
export function useToolConfigs() {
  return useQuery({
    queryKey: ["tool-configs"],
    queryFn: getToolConfigs,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes garbage collection time
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * TanStack Query hook for fetching a single tool configuration
 * @param provider - The tool provider identifier
 * @returns Query result with tool configuration or null
 */
export function useToolConfig(provider: ToolProvider) {
  return useQuery({
    queryKey: ["tool-config", provider],
    queryFn: () => getToolConfig(provider),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes garbage collection time
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}
