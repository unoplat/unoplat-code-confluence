import React, { useState, useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "@tanstack/react-form";
import {
  submitGitHubToken,
  updateGitHubToken,
  ApiError,
  ApiResponse,
} from "@/lib/api";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { Dialog, DialogContent, DialogDescription } from "../ui/dialog";
import { Github, X, ExternalLink, Key } from "lucide-react";
import { useAuthStore } from "@/stores/useAuthStore";
import { buildGitHubPatLink } from "@/lib/github-token-utils";
import { Separator } from "../ui/separator";
import { DEFAULT_REPOSITORY_CREDENTIAL_PARAMS } from "@/lib/constants/credentials";

interface GitHubTokenPopupProps {
  open: boolean;
  onClose: () => void;
  isUpdate?: boolean;
  onSuccess?: () => void;
}

/**
 * GitHub Token Popup Component
 *
 * This component serves as a popup for GitHub token entry and updates
 */
export default function GitHubTokenPopup({
  open,
  onClose,
  isUpdate = false,
  onSuccess,
}: GitHubTokenPopupProps): React.ReactElement {
  console.log("[GitHubTokenPopup] Rendering with props:", { open, isUpdate });

  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<ApiError | null>(null);
  const [formSubmitted, setFormSubmitted] = useState<boolean>(false);
  const [isSuccessful, setIsSuccessful] = useState<boolean>(false);

  // Use Zustand store for token status
  const tokenStatus = useAuthStore((state) => state.tokenStatus);

  // Auto-open dialog when token is not submitted (let parent control open prop)
  useEffect(() => {
    if (tokenStatus && !tokenStatus.status && !formSubmitted && !isSuccessful) {
      console.log(
        "[GitHubTokenPopup] Token not submitted, should open dialog (parent should control)",
      );
      // Parent should set open=true
    }
  }, [tokenStatus, formSubmitted, isSuccessful]);

  // Create form instance
  const form = useForm({
    defaultValues: {
      patToken: "",
    },
    onSubmit: async ({ value }): Promise<void> => {
      console.log(
        "[GitHubTokenPopup] Form submitted with value length:",
        value.patToken ? value.patToken.length : 0,
      );

      const token: string = value.patToken.trim();
      if (!token) {
        console.log("[GitHubTokenPopup] Token is empty, showing error");
        setError({
          message: "Please enter a valid PAT token",
          isAxiosError: false,
        });
        return;
      }

      setFormSubmitted(true);
      setError(null);

      console.log("[GitHubTokenPopup] Calling mutation with token");
      try {
        await tokenMutation.mutateAsync(token);
      } catch (err) {
        console.error("[GitHubTokenPopup] Mutation threw error:", err);
        // Error handling is done in mutation's onError
      }
    },
  });

  const tokenMutation = useMutation<ApiResponse, ApiError, string>({
    mutationFn: (token: string) => {
      return isUpdate
        ? updateGitHubToken(token, DEFAULT_REPOSITORY_CREDENTIAL_PARAMS)
        : submitGitHubToken(token, DEFAULT_REPOSITORY_CREDENTIAL_PARAMS);
    },
    onSuccess: async (): Promise<void> => {
      console.log(
        "[GitHubTokenPopup] Mutation successful, clearing error and resetting form",
      );
      setError(null);
      form.reset();
      setFormSubmitted(false);
      setIsSuccessful(true);

      try {
        console.log("[GitHubTokenPopup] Fetching updated token status");
        // Invalidate the token query to refresh the token status
        await queryClient.invalidateQueries({
          queryKey: ["flags", "isTokenSubmitted"],
        });
        // Also invalidate user data since token has changed
        await queryClient.invalidateQueries({ queryKey: ["githubUser"] });

        if (onSuccess) {
          console.log("[GitHubTokenPopup] Calling onSuccess callback");
          onSuccess();
        }

        // Always close dialog after success
        onClose();

        if (!isUpdate && !onSuccess) {
          console.log("[GitHubTokenPopup] Navigating to /onboarding");
          navigate({ to: "/onboarding" });
        }
      } catch (error) {
        console.error("[GitHubTokenPopup] Error fetching token status:", error);
        setFormSubmitted(false);
        setIsSuccessful(false);
      }
    },
    onError: (error: unknown): void => {
      console.error("[GitHubTokenPopup] Mutation error:", error);
      setFormSubmitted(false);
      setIsSuccessful(false);

      if ((error as ApiError).message) {
        console.log(
          "[GitHubTokenPopup] Setting API error:",
          (error as ApiError).message,
        );
        setError(error as ApiError);
      } else {
        console.log("[GitHubTokenPopup] Setting generic error");
        setError({
          message: "Failed to submit token. Please try again.",
          isAxiosError: false,
        });
      }
    },
  });

  // Reset form when dialog opens
  useEffect(() => {
    if (open) {
      console.log("[GitHubTokenPopup] Dialog opened, initializing form");
      // Only reset if not currently submitting
      if (!formSubmitted) {
        setError(null);
        form.reset();
        setIsSuccessful(false);
      }
    }
  }, [open, form, formSubmitted]);

  // Handle dialog closing
  const handleClose = (): void => {
    console.log("[GitHubTokenPopup] handleClose called");
    // Reset form state
    setError(null);
    form.reset();
    setFormSubmitted(false);
    setIsSuccessful(false);
    // Notify parent
    onClose();
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(open: boolean): void => {
        console.log("[GitHubTokenPopup] Dialog onOpenChange:", open);
        if (!open) {
          handleClose();
        }
      }}
    >
      <DialogContent className="sm:max-w-lg">
        <div className="absolute top-4 right-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClose}
            className="h-6 w-6 rounded-md"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <DialogDescription className="sr-only">
          Enter your GitHub Personal Access Token to authenticate with GitHub.
        </DialogDescription>
        <div className="flex flex-col items-center gap-6 p-2">
          <div className="flex w-full items-center justify-center gap-3">
            <div className="bg-primary/10 flex h-10 w-10 items-center justify-center rounded-full">
              <Github className="text-primary h-5 w-5" />
            </div>
            <h2 className="text-xl font-semibold">GitHub Authentication</h2>
          </div>

          {error && (
            <Alert variant="destructive" className="w-full">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                {error.message}
                {error.statusCode && (
                  <span className="mt-1 block text-xs">
                    Status: {error.statusCode}
                  </span>
                )}
              </AlertDescription>
            </Alert>
          )}

          {/* Step indicator or instructions */}
          <div className="w-full space-y-4">
            <div className="bg-muted/50 space-y-3 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="bg-primary/10 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full">
                  <span className="text-primary text-sm font-semibold">1</span>
                </div>
                <div className="flex-1 space-y-2">
                  <h3 className="font-medium">Generate a GitHub Token</h3>
                  <p className="text-muted-foreground text-sm">
                    Click the button below to open GitHub and create a new
                    Personal Access Token with the required permissions.
                  </p>
                  <Button variant="outline" size="sm" className="gap-2" asChild>
                    <a
                      href={buildGitHubPatLink()}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Key className="h-4 w-4" />
                      Generate Token on GitHub
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </Button>
                  {/* <div className="text-xs text-muted-foreground space-y-1 pt-2">
                    <p className="font-medium">Required permissions:</p>
                    <ul className="list-disc list-inside space-y-0.5 ml-2">
                      {Object.entries(SCOPE_DESCRIPTIONS).map(([scope, description]) => (
                        <li key={scope}>
                          <code className="text-xs bg-muted px-1 rounded">{scope}</code> - {description}
                        </li>
                      ))}
                    </ul>
                  </div> */}
                </div>
              </div>
            </div>

            <Separator />

            <div className="bg-muted/50 space-y-3 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="bg-primary/10 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full">
                  <span className="text-primary text-sm font-semibold">2</span>
                </div>
                <div className="flex-1">
                  <h3 className="mb-3 font-medium">Paste Your Token</h3>
                  <form
                    onSubmit={(e: React.FormEvent<HTMLFormElement>): void => {
                      console.log(
                        "[GitHubTokenPopup] Form onSubmit event triggered",
                      );
                      e.preventDefault();
                      e.stopPropagation();
                      void form.handleSubmit();
                    }}
                    className="space-y-4"
                  >
                    <form.Field
                      name="patToken"
                      validators={{
                        onChange: ({ value }): string | undefined => {
                          const result: string | undefined =
                            value.trim() === ""
                              ? "A GitHub token is required"
                              : undefined;
                          console.log(
                            "[GitHubTokenPopup] Field validation:",
                            result ? "invalid" : "valid",
                          );
                          return result;
                        },
                      }}
                    >
                      {(field): React.ReactElement => (
                        <div className="space-y-2">
                          <Label
                            htmlFor={`github-${field.name}`}
                            className="text-sm font-medium"
                          >
                            GitHub Personal Access Token
                          </Label>
                          <Input
                            type="password"
                            id={`github-${field.name}`}
                            name={field.name}
                            value={field.state.value}
                            onBlur={field.handleBlur}
                            onChange={(
                              e: React.ChangeEvent<HTMLInputElement>,
                            ): void => {
                              console.log("[GitHubTokenPopup] Input changed");
                              field.handleChange(e.target.value);
                              // Clear the error state when user types
                              if (error) {
                                setError(null);
                              }
                            }}
                            placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                            className="w-full font-mono text-sm"
                            autoComplete="off"
                          />
                          {field.state.meta.errors ? (
                            <p className="text-destructive text-sm">
                              {field.state.meta.errors}
                            </p>
                          ) : (
                            <p className="text-muted-foreground text-xs">
                              Your token will be encrypted and stored securely.
                            </p>
                          )}
                        </div>
                      )}
                    </form.Field>

                    <form.Subscribe
                      selector={(state) =>
                        [
                          state.canSubmit,
                          state.isSubmitting,
                          tokenMutation.isPending,
                          formSubmitted,
                        ] as [boolean, boolean, boolean, boolean]
                      }
                    >
                      {(tuple): React.ReactElement => {
                        const [
                          canSubmit,
                          isSubmitting,
                          isMutating,
                          isFormSubmitted,
                        ] = tuple as [boolean, boolean, boolean, boolean];
                        console.log("[GitHubTokenPopup] Button state:", {
                          canSubmit,
                          isSubmitting,
                          isMutating,
                          isFormSubmitted,
                        });

                        return (
                          <Button
                            type="submit"
                            disabled={
                              !canSubmit ||
                              isSubmitting ||
                              isMutating ||
                              isFormSubmitted
                            }
                            className="w-full"
                          >
                            {isSubmitting || isMutating
                              ? "Submitting..."
                              : isUpdate
                                ? "Update Token"
                                : "Submit Token"}
                          </Button>
                        );
                      }}
                    </form.Subscribe>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
