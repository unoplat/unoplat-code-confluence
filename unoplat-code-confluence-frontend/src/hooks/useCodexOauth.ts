import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  authorizeCodexOpenAiOauth,
  disconnectCodexOpenAiOauth,
  getCodexOpenAiOauthStatus,
} from "@/lib/api";

interface CodexOauthPopupResult {
  type: "codex-oauth-callback";
  status: "success" | "failed";
  error?: string;
}

export const useCodexOauth = (enabled = true) => {
  const queryClient = useQueryClient();
  const invalidateModelQueries = React.useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["codex-oauth-status"] });
    queryClient.invalidateQueries({ queryKey: ["model-config"] });
    queryClient.invalidateQueries({ queryKey: ["model-providers"] });
  }, [queryClient]);

  const statusQuery = useQuery({
    queryKey: ["codex-oauth-status"],
    queryFn: getCodexOpenAiOauthStatus,
    enabled,
    staleTime: 15_000,
    retry: 2,
  });

  const authorizeMutation = useMutation({
    mutationFn: authorizeCodexOpenAiOauth,
    onError: (error: Error) => {
      toast.error("Failed to start ChatGPT OAuth", {
        description: error.message || "Unexpected error",
      });
    },
  });

  const disconnectMutation = useMutation({
    mutationFn: disconnectCodexOpenAiOauth,
    onSuccess: (data) => {
      invalidateModelQueries();
      toast.success(data.message || "Disconnected ChatGPT OAuth");
    },
    onError: (error: Error) => {
      toast.error("Failed to disconnect ChatGPT OAuth", {
        description: error.message || "Unexpected error",
      });
    },
  });

  const waitForPopupResult = React.useCallback(
    (
      popup: Window,
      expectedOrigin: string,
      timeoutMs = 5 * 60 * 1000,
    ): Promise<CodexOauthPopupResult> =>
      new Promise((resolve, reject) => {
        let completed = false;

        const cleanup = () => {
          window.removeEventListener("message", onMessage);
          window.clearInterval(intervalId);
          window.clearTimeout(timeoutId);
        };

        const onMessage = (event: MessageEvent) => {
          if (event.origin !== expectedOrigin) {
            return;
          }
          const data = event.data as CodexOauthPopupResult | undefined;
          if (!data || data.type !== "codex-oauth-callback") {
            return;
          }
          completed = true;
          cleanup();
          resolve(data);
        };

        const intervalId = window.setInterval(() => {
          if (popup.closed && !completed) {
            cleanup();
            reject(
              new Error("OAuth popup was closed before completing login."),
            );
          }
        }, 500);

        const timeoutId = window.setTimeout(() => {
          cleanup();
          reject(new Error("OAuth popup timed out."));
        }, timeoutMs);

        window.addEventListener("message", onMessage);
      }),
    [],
  );

  return {
    statusQuery,
    authorizeMutation,
    disconnectMutation,
    invalidateModelQueries,
    waitForPopupResult,
  };
};
