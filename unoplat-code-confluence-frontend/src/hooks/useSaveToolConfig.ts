import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { saveToolConfig, deleteToolConfig } from "@/lib/api/tool-config-api";
import type {
  ToolProvider,
  ToolConfigResponse,
} from "@/features/tool-config/types";

interface SaveToolConfigVariables {
  provider: ToolProvider;
  apiKey: string;
}

interface DeleteToolConfigVariables {
  provider: ToolProvider;
}

/**
 * TanStack Mutation hook for saving tool configuration
 * @returns Mutation object with mutate, isPending, isSuccess, isError states
 */
export function useSaveToolConfig() {
  const queryClient = useQueryClient();

  return useMutation<ToolConfigResponse, Error, SaveToolConfigVariables>({
    mutationFn: async ({ provider, apiKey }) => {
      return await saveToolConfig(provider, apiKey);
    },

    onSuccess: (_data, variables) => {
      // Invalidate and refetch tool config data
      queryClient.invalidateQueries({ queryKey: ["tool-configs"] });
      queryClient.invalidateQueries({
        queryKey: ["tool-config", variables.provider],
      });

      toast.success("Tool configuration saved successfully");
    },

    onError: (error) => {
      toast.error("Failed to save tool configuration", {
        description: error.message || "An unexpected error occurred",
      });
    },

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
}

/**
 * TanStack Mutation hook for deleting tool configuration
 * @returns Mutation object with mutate, isPending, isSuccess, isError states
 */
export function useDeleteToolConfig() {
  const queryClient = useQueryClient();

  return useMutation<{ message: string }, Error, DeleteToolConfigVariables>({
    mutationFn: async ({ provider }) => {
      return await deleteToolConfig(provider);
    },

    onSuccess: (data, variables) => {
      // Invalidate and refetch tool config data
      queryClient.invalidateQueries({ queryKey: ["tool-configs"] });
      queryClient.invalidateQueries({
        queryKey: ["tool-config", variables.provider],
      });

      toast.success(data.message || "Tool configuration deleted successfully");
    },

    onError: (error) => {
      toast.error("Failed to delete tool configuration", {
        description: error.message || "An unexpected error occurred",
      });
    },

    retry: (failureCount, error) => {
      // Don't retry validation errors
      if (
        error.message.includes("validation") ||
        error.message.includes("400") ||
        error.message.includes("404")
      ) {
        return false;
      }
      return failureCount < 2;
    },

    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}
