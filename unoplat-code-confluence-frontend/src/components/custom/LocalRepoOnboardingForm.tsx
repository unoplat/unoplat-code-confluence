"use client";

import React, { useRef, useState } from "react";
import { useForm } from "@tanstack/react-form";
import { Folder, InfoIcon, ArrowRight } from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import {
  validateGitRepositorySync,
  type DirectoryInput,
} from "@/lib/utils/git-validation";
import { RepositoryConfigDialog } from "./RepositoryConfigDialog";
import type { RepositoryConfigDialogData } from "@/types";

// Type declaration for webkitdirectory attribute
declare module 'react' {
  interface HTMLAttributes<T> extends AriaAttributes, DOMAttributes<T> {
    webkitdirectory?: string;
  }
}

export function LocalRepoOnboardingForm(): React.ReactElement {
  console.log("[LocalRepoOnboardingForm] Component rendering");
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  // Ref to store the selected FileList for validation
  const selectedDirRef = useRef<DirectoryInput | null>(null);
  
  // State for repository config dialog
  const [isConfigDialogOpen, setIsConfigDialogOpen] = useState(false);
  const [repositoryConfig, setRepositoryConfig] = useState<RepositoryConfigDialogData | null>(null);

  // Initialize form with TanStack Form using declarative validation
  const form = useForm({
    defaultValues: {
      repositoryPath: "",
    },
    onSubmit: async ({ value }) => {
      console.log("[LocalRepoOnboardingForm] Form onSubmit triggered with values:", value);
      console.log("[LocalRepoOnboardingForm] selectedDirRef.current:", selectedDirRef.current);
      
      if (value.repositoryPath) {
        // Repository name is just the folder name since we now send only that
        const repositoryName = value.repositoryPath;
        
        // Create repository configuration for local repository
        const config: RepositoryConfigDialogData = {
          repositoryName,
          repositoryGitUrl: value.repositoryPath, // Just the folder name for local repos
          repositoryOwnerName: "local", // Default owner for local repos
          isLocal: true,
          localPath: value.repositoryPath, // Just the folder name - backend constructs full path
        };
        
        console.log("[LocalRepoOnboardingForm] Opening RepositoryConfigDialog with config:", config);
        setRepositoryConfig(config);
        setIsConfigDialogOpen(true);
      } else {
        console.log("[LocalRepoOnboardingForm] No repository path in form values");
      }
    },
  });

  console.log("[LocalRepoOnboardingForm] Form state:", {
    values: form.state.values,
    canSubmit: form.state.canSubmit,
    isSubmitting: form.state.isSubmitting,
    errors: form.state.errors,
  });

  // Directory selection using webkitdirectory
  const handleDirectorySelection = (event: React.ChangeEvent<HTMLInputElement>): void => {
    console.log("[LocalRepoOnboardingForm] handleDirectorySelection called");
    
    const files = event.target.files;
    console.log("[LocalRepoOnboardingForm] Selected files:", files);
    console.log("[LocalRepoOnboardingForm] Files length:", files?.length);
    
    if (!files || files.length === 0) {
      console.log("[LocalRepoOnboardingForm] No files selected, returning");
      return;
    }

    try {
      // Get the first file to extract the directory path
      const firstFile = files[0];
      console.log("[LocalRepoOnboardingForm] First file:", firstFile);
      
      const webkitRelativePath = firstFile.webkitRelativePath;
      console.log("[LocalRepoOnboardingForm] webkitRelativePath:", webkitRelativePath);
      
      // Extract the root directory path
      const pathParts = webkitRelativePath.split("/");
      console.log("[LocalRepoOnboardingForm] pathParts:", pathParts);
      
      const folderName = pathParts[0];
      console.log("[LocalRepoOnboardingForm] Extracted folderName:", folderName);
      
      // Send just the folder name - backend will construct the appropriate path based on environment
      const repositoryPath = folderName;
      console.log("[LocalRepoOnboardingForm] Repository folder name:", repositoryPath);

      // Validate the repository synchronously before setting form value
      console.log("[LocalRepoOnboardingForm] Validating repository synchronously...");
      const isValid = validateGitRepositorySync(files);
      console.log("[LocalRepoOnboardingForm] Repository validation result:", isValid);
      
      if (!isValid) {
        console.log("[LocalRepoOnboardingForm] Repository validation failed");
        toast.error("No Git repository found. Please select a folder containing a .git directory.");
        
        // Clear the field value and reset the selected directory ref
        selectedDirRef.current = null;
        form.setFieldValue('repositoryPath', '');
        
        return;
      }

      // Store the FileList for validation
      selectedDirRef.current = files;
      console.log("[LocalRepoOnboardingForm] Stored files in selectedDirRef");
      
      // Update form field value - validation will trigger validator
      console.log("[LocalRepoOnboardingForm] Setting form field value to:", repositoryPath);
      form.setFieldValue('repositoryPath', repositoryPath);
      console.log("[LocalRepoOnboardingForm] Form field value set successfully");
      
      // Show success toast
      toast.success("Git repository validated successfully!");
      
    } catch (error) {
      console.error("[LocalRepoOnboardingForm] Error processing directory:", error);
      toast.error("Failed to process the selected directory.");
    }
  };

  return (
    <>
    <Card variant="default" padding="lg" radius="lg">
      <CardHeader>
        <CardTitle>Local Repository</CardTitle>
        <CardDescription>
          Select a local Git repository to analyze and configure its codebases. 
          <br />
          <strong>Note:</strong> Please ensure your repository is located in the directory configured by the backend's <code>REPOSITORIES_BASE_PATH</code> setting.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e: React.FormEvent<HTMLFormElement>) => {
            console.log("[LocalRepoOnboardingForm] Form submit event triggered");
            e.preventDefault();
            console.log("[LocalRepoOnboardingForm] Calling form.handleSubmit()");
            form.handleSubmit();
          }}
          className="space-y-6"
        >
          {/* Repository Path Input */}
          <form.Field
            name="repositoryPath"
            validators={{
              onChange: ({ value }): string | undefined => {
                console.log("[LocalRepoOnboardingForm] Sync onChange validator called with value:", value);
                if (!value || value.trim() === "") {
                  return "Please select a valid Git repository";
                }
                if (!selectedDirRef.current) {
                  return "Please use the Browse button to select a repository";
                }
                // Re-validate the repository to ensure it's still valid
                console.log("[LocalRepoOnboardingForm] Re-validating repository in onChange...");
                const isValid = validateGitRepositorySync(selectedDirRef.current);
                console.log("[LocalRepoOnboardingForm] Re-validation result:", isValid);
                return isValid ? undefined : "No Git repository found. Please select a folder containing a .git directory.";
              },
            }}
          >
            {(field) => {
              console.log("[LocalRepoOnboardingForm] Field render function called");
              console.log("[LocalRepoOnboardingForm] Field state:", {
                value: field.state.value,
                meta: field.state.meta,
                errors: field.state.meta.errors,
                isValidating: field.state.meta.isValidating,
              });

              return (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="repoPath" className="text-sm font-medium">
                      Repository Path <span className="text-destructive">*</span>
                    </Label>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="inline-flex">
                            <InfoIcon className="h-4 w-4 text-muted-foreground cursor-pointer" />
                          </span>
                        </TooltipTrigger>
                        <TooltipContent side="right" align="start" className="max-w-[300px] text-sm">
                          <p>
                            Select a folder that contains a Git repository (.git folder) from the directory configured by the backend's <code>REPOSITORIES_BASE_PATH</code> setting. 
                            The system will automatically detect the correct path based on your environment and volume mount configuration.
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                  <div className="flex space-x-2">
                    <Input
                      id="repoPath"
                      name={field.name}
                      value={field.state.value}
                      onBlur={() => {
                        console.log("[LocalRepoOnboardingForm] Input onBlur called");
                        field.handleBlur();
                      }}
                      readOnly
                      placeholder="Select a local git repository folder..."
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        console.log("[LocalRepoOnboardingForm] Browse button clicked");
                        console.log("[LocalRepoOnboardingForm] fileInputRef.current:", fileInputRef.current);
                        fileInputRef.current?.click();
                      }}
                      className="px-4"
                    >
                      <Folder className="mr-2 h-4 w-4" />
                      Browse
                    </Button>
                  </div>
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {(() => {
                        const errs = field.state.meta.errors;
                        console.log("[LocalRepoOnboardingForm] Field errors:", errs);
                        
                        const hasPending = errs.some(
                          (e) => e && typeof e === 'object' && 'then' in e,
                        );
                        console.log("[LocalRepoOnboardingForm] Has pending validation:", hasPending);
                        
                        if (hasPending) {
                          console.log("[LocalRepoOnboardingForm] Showing 'Validation in progress...'");
                          return 'Validation in progress…';
                        }
                        
                        const errorText = Array.from(new Set(errs.map(String))).join(', ');
                        console.log("[LocalRepoOnboardingForm] Showing error text:", errorText);
                        return errorText;
                      })()}
                    </p>
                  )}
                </div>
              );
            }}
          </form.Field>

          {/* Hidden file input for directory selection */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => {
              console.log("[LocalRepoOnboardingForm] Hidden file input onChange triggered");
              handleDirectorySelection(e);
            }}
            webkitdirectory="true"
            multiple
            className="hidden"
            aria-hidden="true"
          />

          {/* Continue Button */}
          <form.Subscribe
            selector={(state) => [state.canSubmit, state.isSubmitting]}
            children={([canSubmit, isSubmitting]) => {
              console.log("[LocalRepoOnboardingForm] Subscribe render - canSubmit:", canSubmit, "isSubmitting:", isSubmitting);
              
              return (
                <div className="flex justify-end">
                  <Button
                    type="submit"
                    disabled={!canSubmit}
                    size="sm"
                    className="px-6"
                    onClick={() => {
                      console.log("[LocalRepoOnboardingForm] Continue button clicked");
                      console.log("[LocalRepoOnboardingForm] Button disabled state:", !canSubmit);
                    }}
                  >
                    <ArrowRight className="mr-2 h-4 w-4" />
                    {isSubmitting ? "Processing..." : "Continue to Configuration"}
                  </Button>
                </div>
              );
            }}
          />

        </form>
      </CardContent>
    </Card>

    {/* Repository Configuration Dialog */}
    {repositoryConfig && (
      <RepositoryConfigDialog
        repositoryName={repositoryConfig.repositoryName}
        repositoryGitUrl={repositoryConfig.repositoryGitUrl}
        repositoryOwnerName={repositoryConfig.repositoryOwnerName}
        isOpen={isConfigDialogOpen}
        onOpenChange={(open) => {
          setIsConfigDialogOpen(open);
          if (!open) {
            setRepositoryConfig(null);
          }
        }}
        isLocal={repositoryConfig.isLocal}
        localPath={repositoryConfig.localPath}
      />
    )}
    </>
  );
}