"use client";

import { z } from "zod";
import { useForm } from "@tanstack/react-form";
import { PlusIcon } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getRepositoryConfig, submitRepositoryConfig } from '../../lib/api';
import type { GitHubRepoRequestConfiguration, GitHubRepoResponseConfiguration, CodebaseRepoConfig, ApiResponse } from '../../types';
import React from 'react';
import axios from 'axios';

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
import { CodebaseSchema, type Codebase } from "./CodebaseForm";
import { toast } from "sonner";


// Schema for a repository configuration containing multiple codebases
export const RepositoryConfigSchema = z.object({
  repositoryName: z.string(),
  repositoryGitUrl: z.string(),
  repositoryOwnerName: z.string(),
  codebases: z.array(CodebaseSchema).min(1, "At least one codebase is required"),
});

export type RepositoryConfig = z.infer<typeof RepositoryConfigSchema>;

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
  const queryClient = useQueryClient(); 
  
  // Local dialog open/close handler
  function handleDialogOpenChange(open: boolean): void {
    console.log('[RepositoryConfigDialog] Dialog open/close handler called with open:', open);
    if (!open) {
      form.reset();
    }
    onOpenChange(open);
  }

  // Default codebase structure
  const defaultCodebase: Codebase = {
    codebase_folder: "",
    root_package: "",
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
          root_package: item.root_package || "",
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
  
  // Disable update functionality until backend supports it
  /*
  const updateMutation = useMutation<ApiResponse, Error, GitHubRepoRequestConfiguration>({
    mutationFn: updateRepositoryData,
    onSuccess: () => {
      // Invalidate all repository configurations to force a refetch
      queryClient.invalidateQueries({ queryKey: ["repository-config"] });
      // Also invalidate the specific repository config
      queryClient.invalidateQueries({ queryKey: ["repository-config", repositoryName] });
      toast.success(`Successfully updated repository configuration for ${repositoryName}`);
      // Close the dialog and reset the form
      handleDialogOpenChange(false);
      form.reset();
    },
    onError: (error) => {
      console.error("Failed to update repository data:", error);
      toast.error(`Failed to update repository configuration: ${error.message}`);
    },
  });
  */

  // Initialize form with TanStack Form
  const form = useForm({
    defaultValues: {
      repositoryName,
      codebases: existingCodebases || [defaultCodebase],
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
            root_package: cb.root_package || "",
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

  // Explicitly reset the form when initialCodebases change
  React.useEffect(() => {
    if (isOpen) {
      console.log('[RepositoryConfigDialog] Resetting form with initialCodebases', existingCodebases);
      form.reset({
        repositoryName,
        codebases: existingCodebases || [defaultCodebase],
      });
    }
  }, [existingCodebases, isOpen, repositoryName, form]);

  // Create button text based on configuration existence
  const buttonText: string = "Submit Repo";

  

  if (isLoadingConfig) {
    return (
      <Dialog open={isOpen} onOpenChange={handleDialogOpenChange}>
        <DialogContent>
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
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Error loading configuration</DialogTitle>
          </DialogHeader>
          <div className="py-8 text-center text-destructive">{String(errorConfig)}</div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleDialogOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Configure Repository: {repositoryName}</DialogTitle>
          <DialogDescription>
            Configure one or more codebases for this repository. Each codebase represents a separate project within the repository.
          </DialogDescription>
        </DialogHeader>

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
                          className="flex items-center justify-center bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100"
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
              className="border-muted bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground focus-visible:ring-2 focus-visible:ring-ring"
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
      </DialogContent>
    </Dialog>
  );
} 