"use client";


import { useForm } from "@tanstack/react-form";
import { PlusIcon, Wand2Icon, Loader2Icon, AlertCircleIcon, InfoIcon } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getRepositoryConfig, submitRepositoryConfig } from '../../lib/api';
import type { GitHubRepoRequestConfiguration, GitHubRepoResponseConfiguration, CodebaseRepoConfig, ApiResponse } from '../../types';
import React, { useState } from 'react';
import axios from 'axios';
import { useDetectCodebases } from '@/hooks/useDetectCodebases';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { CodebaseForm } from "./CodebaseForm";
import { type Codebase } from "./CodebaseForm";
import { toast } from "sonner";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";




interface RepositoryConfigDialogProps {
  repositoryName: string;
  repositoryGitUrl: string;
  repositoryOwnerName: string;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function RepositoryConfigDialog({
  repositoryName,
  repositoryGitUrl,
  repositoryOwnerName,
  isOpen,
  onOpenChange,
}: RepositoryConfigDialogProps): React.ReactElement {
  // Local dialog/detection state
  const [dialogMode, setDialogMode] = useState<'initial' | 'detecting' | 'configuring'>('initial');

  const {
    cancelDetection,
    status: detectionStatus,
    error: detectionError,
    codebases: detectedCodebases,
  } = useDetectCodebases({
    gitUrl: dialogMode === 'detecting' ? repositoryGitUrl : null,
    onSuccess: () => {
      toast.success('Codebase detection completed successfully!');
      setDialogMode('configuring');
    },
    onError: (err) => {
      // The shape of the error chunk can vary depending on the backend. We
      // guard against unexpected structures to avoid runtime failures.
      const message =
        typeof err === 'string'
          ? err
          : err && typeof err === 'object' && 'error' in err && err.error
            ? (err as { error: string }).error
            : 'Unknown error';

      toast.error(`Detection failed: ${message}`);
      setDialogMode('initial');
    },
  });
  const queryClient = useQueryClient(); 
  
  // Local dialog open/close handler
  function handleDialogOpenChange(open: boolean): void {
    console.log('[RepositoryConfigDialog] Dialog open/close handler called with open:', open);
    if (!open) {
      form.reset();
      cancelDetection();
      setDialogMode('initial');
    }
    onOpenChange(open);
  }

  // Default codebase structure
  const defaultCodebase: Codebase = {
    codebase_folder: "",
    root_packages: null,
    programming_language_metadata: {
      language: "python",
      package_manager: "uv",
    }
  };

  // Fetch existing configuration from backend
  const {
    data: loadedConfig,
    isLoading: isLoadingConfig,
    isError: isErrorConfig,
    error: errorConfig,
  } = useQuery<GitHubRepoResponseConfiguration | null>({
    queryKey: ["repository-config", repositoryName],
    queryFn: () => getRepositoryConfig(repositoryName, repositoryOwnerName),
    enabled: isOpen && repositoryName.length > 0,
    staleTime: 0, // Consider data always stale to force refetch when dialog opens
    refetchOnWindowFocus: false,
    gcTime: 0, // Don't cache the data between dialog openings (using gcTime instead of cacheTime in v5)
  });

  
  // Extract codebases from loadedConfig if available
  const existingCodebases = React.useMemo(() => {
    if (loadedConfig && Array.isArray(loadedConfig.repository_metadata)) {
      return loadedConfig.repository_metadata.map((item: CodebaseRepoConfig) => {
        // Convert to the expected Codebase type
        const codebase: Codebase = {
          codebase_folder: item.codebase_folder || "",
          root_packages: item.root_packages || null,
          programming_language_metadata: {
            language: item.programming_language_metadata.language || "python",
            package_manager: item.programming_language_metadata.package_manager || "uv",
          }
        };
        return codebase;
      });
    }
    return [];
  }, [loadedConfig]);

  // Automatically switch to configuring mode if we have existing config
  React.useEffect(() => {
    if (existingCodebases.length > 0 && dialogMode === 'initial' && !isLoadingConfig) {
      setDialogMode('configuring');
    }
  }, [existingCodebases.length, dialogMode, isLoadingConfig]);

  // Mutation for create
  const createMutation = useMutation<ApiResponse, Error, GitHubRepoRequestConfiguration>({
    mutationFn: submitRepositoryConfig,
    onSuccess: () => {
      // Invalidate all repository configurations to force a refetch
      queryClient.invalidateQueries({ queryKey: ["repository-config"] });
      
      // Also invalidate the specific repository config
      queryClient.invalidateQueries({ 
        queryKey: ["repository-config", repositoryName] 
      });
      
      toast.success(`Successfully submitted repository ${repositoryName} to code confluence graph engine`);
      
      // Close the dialog and reset the form
      handleDialogOpenChange(false);
      form.reset();
    },
    onError: (error: Error) => {
      console.error("Failed to submit repository:", error);
      toast.error(`Failed to submit repository : ${error.message}`);
    },
  });
  
  
  // Initialize form with TanStack Form
  const form = useForm({
    defaultValues: {
      repositoryName,
      codebases: existingCodebases.length > 0 ? existingCodebases : [defaultCodebase],
    },
    onSubmit: async ({ value }) => {
      console.log('[RepositoryConfigDialog] Form submitted with values:', value);
      try {
        // Map form values to API payload format
        const payload: GitHubRepoRequestConfiguration = {
          repository_name: value.repositoryName,
          repository_git_url: repositoryGitUrl,
          repository_owner_name: repositoryOwnerName,
          repository_metadata: value.codebases.map((cb) => ({
            codebase_folder: cb.codebase_folder,
            root_packages: cb.root_packages || null,
            programming_language_metadata: cb.programming_language_metadata,
          })),
        };

        // Check if we're updating or creating
        // const hasExistingConfig = existingConfig || (loadedConfig && loadedConfig.repository_metadata && loadedConfig.repository_metadata.length > 0);
        
        // if (hasExistingConfig) {
        //   console.log('[RepositoryConfigDialog] Calling update mutation');
        //   await updateMutation.mutateAsync(payload);
        // } else {
          console.log('[RepositoryConfigDialog] Calling create mutation');
          await createMutation.mutateAsync(payload);
        // }
        
        // Call the onSave callback if provided
        // onSave({
        //   repositoryName: value.repositoryName,
        //   repositoryGitUrl: repositoryGitUrl,
        //   repositoryOwnerName: repositoryOwnerName,
        //   codebases: value.codebases,
        // });
        
        // Dialog will close in the mutation's onSuccess handler
      } catch (error) {
        console.error('[RepositoryConfigDialog] Error saving repository configuration:', error);
        
        let errorMessage = 'Failed to save repository configuration';
        if (error instanceof Error) {
          errorMessage = error.message;
        }
        
        toast.error(errorMessage);
        return {
          // Return validation errors if needed - this schema matches TanStack Form's expected error format
          values: Object.fromEntries(
            Object.entries(value).filter(([key]) =>
              key === "repositoryName" || key === "codebases"
            )
          ),
          errors: Object.fromEntries(
            Object.entries({
              "": ["Failed to save repository configuration. Please try again."],
            }).filter(([
              key,
              errors,
            ]) => 
              key === "" || 
              (Array.isArray(errors) && errors.length > 0)
            ).map(([
              key,
              errors,
            ]) => [
              key,
              errors?.join(", ")
            ])
          ),
        };
      }
      return undefined;
    },
  });

  // Workaround for TanStack Form ≥1.9 reset regression -------------------
  // See https://github.com/TanStack/form/issues/1490. We avoid form.reset()
  // with values and instead update defaultValues and current state in one go.
  const prefillForm = React.useCallback(
    (codebasesToApply: Codebase[]) => {
      form.update({
        defaultValues: {
          repositoryName,
          codebases: codebasesToApply,
        },
      });

      // 2) push the same tree into state.values (workaround for reset bug)
      form.setFieldValue('codebases', codebasesToApply);
    },
    [form, repositoryName],
  );

  const didPrefill = React.useRef(false);

  React.useEffect(() => {
    // Reset guard when dialog closes
    if (!isOpen) {
      didPrefill.current = false;
      return;
    }

    if (didPrefill.current) return;

    if (existingCodebases.length > 0) {
      // Prefill with server configuration
      console.debug('[RepositoryConfigDialog] prefill with existing config');
      prefillForm(existingCodebases);
      didPrefill.current = true;
      return;
    }

    if (detectionStatus === 'success' && detectedCodebases.length > 0) {
      // Prefill with detected codebases
      console.debug('[RepositoryConfigDialog] prefill with detected codebases');
      prefillForm(detectedCodebases);
      didPrefill.current = true;
    }
  }, [isOpen, existingCodebases.length, detectionStatus, detectedCodebases.length, prefillForm]);

  // Create button text based on configuration existence
  const buttonText: string = "Submit Repo";

  

  if (isLoadingConfig) {
    return (
      <Dialog open={isOpen} onOpenChange={handleDialogOpenChange}>
        <DialogContent aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Loading configuration...</DialogTitle>
          </DialogHeader>
          <div className="py-8 text-center text-muted-foreground">Loading repository configuration...</div>
        </DialogContent>
      </Dialog>
    );
  }
  
  // Only show error dialog for server errors (5xx), not for 404s which indicate no config exists yet
  if (isErrorConfig && errorConfig instanceof Error && !(axios.isAxiosError(errorConfig) && errorConfig.response?.status === 404)) {
    return (
      <Dialog open={isOpen} onOpenChange={handleDialogOpenChange}>
        <DialogContent aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Error loading configuration</DialogTitle>
          </DialogHeader>
          <div className="py-8 text-center text-destructive">{String(errorConfig)}</div>
        </DialogContent>
      </Dialog>
    );
  }

  // Handle manual configuration
  const handleManualConfig = () => {
    setDialogMode('configuring');
    // If we have detected codebases, use them; otherwise use default
    if (detectedCodebases.length > 0) {
      prefillForm(detectedCodebases);
    }
  };

  // Handle auto-detect
  const handleAutoDetect = () => {
    setDialogMode('detecting');
  };

  // Render content based on dialog mode
  const renderDialogContent = () => {
    switch (dialogMode) {
      case 'initial':
        return (
          <>
            <DialogHeader>
              <DialogTitle className="text-2xl font-semibold tracking-tight">
                Configure Repository: <span className="text-primary">{repositoryName}</span>
              </DialogTitle>
              <DialogDescription className="text-sm leading-6">
                Configure one or more codebases for this repository. Each codebase represents a separate project within the repository.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-3 py-6">
              <Button
                onClick={handleAutoDetect}
                className="w-full h-11 inline-flex items-center justify-center"
                size="lg"
              >
                <Wand2Icon className="mr-2 h-4 w-4" />
                Detect Codebases Automatically
                <Badge variant="secondary" className="ml-2 bg-primary-foreground/20 text-primary-foreground">
                  Beta
                </Badge>
              </Button>
              <Button
                variant="outline"
                onClick={handleManualConfig}
                className="w-full h-11 inline-flex items-center justify-center"
                size="lg"
              >
                <PlusIcon className="mr-2 h-4 w-4" />
                Configure Manually
              </Button>
            </div>
            <div className="rounded-md bg-muted px-4 py-3">
              <p className="text-sm text-muted-foreground">
                <InfoIcon className="mr-2 h-4 w-4 inline-block" />
                Automatic detection helps find Python projects and their main directories. You'll be able to review and edit any suggestions.
              </p>
            </div>
          </>
        );

      case 'detecting':
        return (
          <>
            <DialogHeader>
              <DialogTitle>Detecting Codebases</DialogTitle>
              <DialogDescription>
                Analyzing your repository structure...
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-8">
              <div className="flex items-center justify-center">
                <Loader2Icon className="h-8 w-8 animate-spin text-primary" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-3/4 mx-auto" />
                <Skeleton className="h-4 w-1/2 mx-auto" />
                <Skeleton className="h-4 w-2/3 mx-auto" />
              </div>
              {detectionError && (
                <Alert variant="destructive">
                  <AlertCircleIcon className="h-4 w-4" />
                  <AlertDescription>{detectionError}</AlertDescription>
                </Alert>
              )}
              <div className="text-center text-sm text-muted-foreground">
                {detectionStatus === 'detecting' && 'This may take a few moments...'}
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => { cancelDetection(); setDialogMode('initial'); }}>
                Cancel
              </Button>
            </DialogFooter>
          </>
        );

      case 'configuring':
        return (
          <>
            <DialogHeader>
              <DialogTitle>Configure Repository: {repositoryName}</DialogTitle>
              <DialogDescription id="repo-config-desc">
                {detectionStatus === 'success' && detectedCodebases.length > 0 
                  ? `We detected ${detectedCodebases.length} codebase${detectedCodebases.length > 1 ? 's' : ''} in your repository. Review and modify as needed before submitting.`
                  : 'Configure one or more codebases for this repository. Each codebase represents a separate project within the repository.'
                }
              </DialogDescription>
            </DialogHeader>

            {detectionStatus === 'success' && detectedCodebases.length > 0 && (
              <Alert className="mt-4">
                <Wand2Icon className="h-4 w-4" />
                <AlertDescription>
                  Automatic detection completed successfully. The detected codebases have been pre-filled below.
                </AlertDescription>
              </Alert>
            )}

        <form onSubmit={(e: React.FormEvent<HTMLFormElement>) => {
          e.preventDefault();
          form.handleSubmit();
        }}>
          <div className="py-4 space-y-6">
            <form.Field
              name="codebases"
              mode="array"
            >
              {(field) => {
                const isCreating = existingCodebases.length === 0;
                const allowRemove = isCreating && field.state.value.length > 1;
                return (
                  <>
                    {field.state.value.map((_, index: number) => (
                      <CodebaseForm
                        key={index}
                        index={index}
                        parentForm={form}
                        disabled={!isCreating}
                        onRemove={allowRemove ? () => field.removeValue(index) : undefined}
                      />
                    ))}
                    {/* Hide Add Codebase button if editing existing config */}
                    {existingCodebases.length === 0 && (
                      <div className="flex justify-center mt-4">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          aria-label="Add Codebase"
                          className="flex items-center justify-center"
                          onClick={() => field.pushValue(defaultCodebase)}
                        >
                          <PlusIcon className="mr-2 h-4 w-4" />
                          Add Codebase
                        </Button>
                      </div>
                    )}
                  </>
                );
              }}
            </form.Field>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleDialogOpenChange(false)}
            >
              Cancel
            </Button>
            <form.Subscribe
              selector={(state) => state}
              children={(state) => (
                <Button 
                  type="submit"
                  disabled={!state.canSubmit || state.isSubmitting || existingCodebases.length > 0}
                >
                  {state.isSubmitting 
                    ? "Submitting..."
                    : buttonText
                  }
                </Button>
              )}
            />
          </DialogFooter>
        </form>
          </>
        );
      
      default:
        return null;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleDialogOpenChange}>
      <DialogContent aria-describedby="repo-config-desc" className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        {renderDialogContent()}
      </DialogContent>
    </Dialog>
  );
} 