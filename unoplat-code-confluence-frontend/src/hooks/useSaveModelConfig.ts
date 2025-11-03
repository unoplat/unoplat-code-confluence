import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { saveModelProviderConfig } from "@/lib/api";

interface SaveModelConfigVariables {
  config: Record<string, unknown>;
}

interface SaveModelConfigResponse {
  success: boolean;
  message?: string;
}

/**
 * TanStack Mutation hook for saving model provider configuration
 * Uses simple mutate pattern consistent with existing codebase
 *
 * @returns Mutation object with mutate, isPending, isSuccess, isError states
 */
export const useSaveModelConfig = () => {
  const queryClient = useQueryClient();

  return useMutation<SaveModelConfigResponse, Error, SaveModelConfigVariables>({
    mutationFn: async ({ config }) => {
      return await saveModelProviderConfig(config);
    },

    onSuccess: (data) => {
      // Invalidate and refetch provider data
      queryClient.invalidateQueries({ queryKey: ["model-providers"] });
      queryClient.invalidateQueries({ queryKey: ["model-config"] });

      // Show success toast
      toast.success(
        data.message || "Provider configuration saved successfully",
      );
    },

    onError: (error) => {
      // Show error toast
      toast.error("Failed to save configuration", {
        description: error.message || "An unexpected error occurred",
      });
    },

    // Basic retry for network errors
    retry: (failureCount, error) => {
      // Don't retry validation errors
      if (
        error.message.includes("validation") ||
        error.message.includes("400")
      ) {
        return false;
      }
      return failureCount < 2;
    },

    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

/**
 * Hook for saving configuration for a specific provider
 * Provides a more convenient interface for single provider updates
 *
 * @param providerKey - The provider key to save configuration for
 * @returns Mutation object with simplified mutate function
 */
export const useSaveProviderConfig = (providerKey: string) => {
  const saveConfigMutation = useSaveModelConfig();

  return {
    ...saveConfigMutation,
    mutate: (
      config: Record<string, unknown>,
      options?: Parameters<typeof saveConfigMutation.mutate>[1],
    ) => {
      saveConfigMutation.mutate(
        { config: { ...config, provider_key: providerKey } },
        options,
      );
    },
  };
};
