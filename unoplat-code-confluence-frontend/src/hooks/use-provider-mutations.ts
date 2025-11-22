import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  submitGitHubToken,
  updateGitHubToken,
  deleteGitHubToken,
  type ApiResponse,
} from "@/lib/api";
import type { CredentialParams } from "@/types/credential-enums";

/**
 * Hook providing mutations for provider token operations with automatic cache invalidation
 *
 * Replaces manual Zustand store updates with React Query mutations that:
 * - Handle loading/error states automatically
 * - Invalidate relevant caches on success
 * - Provide consistent error handling
 *
 * @returns Mutation functions for token operations
 *
 * @example
 * ```tsx
 * function TokenForm() {
 *   const { submitToken, updateToken, deleteToken } = useProviderMutations();
 *
 *   const handleSubmit = async (token: string, params: CredentialParams) => {
 *     const result = await submitToken.mutateAsync({ token, params });
 *     if (result.success) {
 *       toast.success("Token submitted successfully");
 *     }
 *   };
 *
 *   return <form onSubmit={handleSubmit}>...</form>;
 * }
 * ```
 */
export function useProviderMutations() {
  const queryClient = useQueryClient();

  const submitToken = useMutation<
    ApiResponse,
    Error,
    { token: string; params: CredentialParams }
  >({
    mutationFn: ({ token, params }) => submitGitHubToken(token, params),
    onSuccess: () => {
      // Invalidate provider list to refetch after successful submission
      void queryClient.invalidateQueries({
        queryKey: ["repository-providers"],
      });
      // Refresh user profile so sidebar avatar updates immediately
      void queryClient.invalidateQueries({
        queryKey: ["githubUser"],
      });
    },
  });

  const updateToken = useMutation<
    ApiResponse,
    Error,
    { token: string; params: CredentialParams }
  >({
    mutationFn: ({ token, params }) => updateGitHubToken(token, params),
    onSuccess: () => {
      // Invalidate provider list to refetch after successful update
      void queryClient.invalidateQueries({
        queryKey: ["repository-providers"],
      });
      void queryClient.invalidateQueries({
        queryKey: ["githubUser"],
      });
    },
  });

  const deleteToken = useMutation<
    ApiResponse,
    Error,
    Omit<CredentialParams, "url">
  >({
    mutationFn: (params) => deleteGitHubToken(params),
    onSuccess: () => {
      // Invalidate both provider list and token status flag
      void queryClient.invalidateQueries({
        queryKey: ["repository-providers"],
      });
      void queryClient.invalidateQueries({
        queryKey: ["githubUser"],
      });
    },
  });

  return {
    submitToken,
    updateToken,
    deleteToken,
  };
}
