import React, { useState, useEffect } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { useForm } from '@tanstack/react-form';
import { submitGitHubToken, ApiError, getFlagStatus } from '../lib/api';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Dialog, DialogContent, DialogDescription } from './ui/dialog';
import { Github, X } from 'lucide-react';
import type { FlagResponse } from '../types';

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
  onSuccess
}: GitHubTokenPopupProps): React.ReactElement {
  console.log('[GitHubTokenPopup] Rendering with props:', { open, isUpdate });
  
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<ApiError | null>(null);
  const [formSubmitted, setFormSubmitted] = useState<boolean>(false);
  const [isSuccessful, setIsSuccessful] = useState<boolean>(false);
  
  // Track the flag status to determine if dialog should be shown
  const { data: flagStatus } = useQuery<FlagResponse>({
    queryKey: ['flags', 'isTokenSubmitted'],
    queryFn: (): Promise<FlagResponse> => {
      console.log('[GitHubTokenPopup] Fetching token flag status');
      return getFlagStatus('isTokenSubmitted');
    }
  });

  // Auto-open dialog when token is not submitted (let parent control open prop)
  useEffect(() => {
    if (flagStatus && !flagStatus.status && !formSubmitted && !isSuccessful) {
      console.log('[GitHubTokenPopup] Token not submitted, should open dialog (parent should control)');
      // Parent should set open=true
    }
  }, [flagStatus, formSubmitted, isSuccessful]);

  // Create form instance
  const form = useForm({
    defaultValues: {
      patToken: '',
    },
    onSubmit: async ({ value }): Promise<void> => {
      console.log('[GitHubTokenPopup] Form submitted with value length:', value.patToken ? value.patToken.length : 0);
      
      const token: string = value.patToken.trim();
      if (!token) {
        console.log('[GitHubTokenPopup] Token is empty, showing error');
        setError({
          message: 'Please enter a valid PAT token',
          isAxiosError: false
        });
        return;
      }
      
      setFormSubmitted(true);
      setError(null);
      
      console.log('[GitHubTokenPopup] Calling mutation with token');
      try {
        await tokenMutation.mutateAsync(token);
      } catch (err) {
        console.error('[GitHubTokenPopup] Mutation threw error:', err);
        // Error handling is done in mutation's onError
      }
    },
  });
  
  const tokenMutation = useMutation({
    mutationFn: submitGitHubToken,
    onSuccess: async (): Promise<void> => {
      console.log('[GitHubTokenPopup] Mutation successful, clearing error and resetting form');
      setError(null);
      form.reset();
      setFormSubmitted(false);
      setIsSuccessful(true);
      
      try {
        console.log('[GitHubTokenPopup] Invalidating token status query');
        await queryClient.invalidateQueries({ queryKey: ['flags', 'isTokenSubmitted'] });
        
        if (onSuccess) {
          console.log('[GitHubTokenPopup] Calling onSuccess callback');
          onSuccess();
        }
        // Always close dialog after success
        onClose();
        if (!isUpdate && !onSuccess) {
          console.log('[GitHubTokenPopup] Navigating to /onboarding');
          navigate({ to: '/onboarding' });
        }
      } catch (error) {
        console.error('[GitHubTokenPopup] Error refreshing flag status:', error);
        setFormSubmitted(false);
        setIsSuccessful(false);
      }
    },
    onError: (error: unknown): void => {
      console.error('[GitHubTokenPopup] Mutation error:', error);
      setFormSubmitted(false);
      setIsSuccessful(false);
      
      if ((error as ApiError).message) {
        console.log('[GitHubTokenPopup] Setting API error:', (error as ApiError).message);
        setError(error as ApiError);
      } else {
        console.log('[GitHubTokenPopup] Setting generic error');
        setError({
          message: 'Failed to submit token. Please try again.',
          isAxiosError: false
        });
      }
    }
  });

  // Reset form when dialog opens
  useEffect(() => {
    if (open) {
      console.log('[GitHubTokenPopup] Dialog opened, initializing form');
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
    console.log('[GitHubTokenPopup] handleClose called');
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
        console.log('[GitHubTokenPopup] Dialog onOpenChange:', open);
        if (!open) {
          handleClose();
        }
      }}
    >
      <DialogContent className="sm:max-w-md">
        <div className="absolute right-4 top-4">
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
        <div className="flex flex-col gap-6 items-center p-2">
          <div className="flex items-center justify-center gap-3 w-full">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
              <Github className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-xl font-semibold">GitHub Authentication</h2>
          </div>
          
          {error && (
            <Alert variant="destructive" className="w-full">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                {error.message}
                {error.statusCode && (
                  <span className="block text-xs mt-1">Status: {error.statusCode}</span>
                )}
              </AlertDescription>
            </Alert>
          )}

          <form
            onSubmit={(e: React.FormEvent<HTMLFormElement>): void => {
              console.log('[GitHubTokenPopup] Form onSubmit event triggered');
              e.preventDefault();
              e.stopPropagation();
              void form.handleSubmit();
            }}
            className="w-full space-y-4"
          >
            <div className="grid w-full gap-2">
              <form.Field
                name="patToken"
                validators={{
                  onChange: ({ value }): string | undefined => {
                    const result: string | undefined = value.trim() === '' ? 'A GitHub token is required' : undefined;
                    console.log('[GitHubTokenPopup] Field validation:', result ? 'invalid' : 'valid');
                    return result;
                  },
                }}
              >
                {(field): React.ReactElement => (
                  <div className="grid gap-1">
                    <Label htmlFor={`github-${field.name}`} className="text-sm font-medium">
                      GitHub Personal Access Token (PAT)
                    </Label>
                    <Input
                      type="password"
                      id={`github-${field.name}`}
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>): void => {
                        console.log('[GitHubTokenPopup] Input changed');
                        field.handleChange(e.target.value);
                        // Clear the error state when user types
                        if (error) {
                          setError(null);
                        }
                      }}
                      placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                      className="w-full"
                      autoComplete="off"
                    />
                    {field.state.meta.errors ? (
                      <p className="text-sm text-destructive">
                        {field.state.meta.errors}
                      </p>
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        Your token will be securely stored and used only for GitHub API requests.
                      </p>
                    )}
                  </div>
                )}
              </form.Field>
            </div>
            <div className="flex flex-col gap-2">
              <form.Subscribe
                selector={(state) => [state.canSubmit, state.isSubmitting, tokenMutation.isPending, formSubmitted] as [boolean, boolean, boolean, boolean]}
              >
                {(tuple): React.ReactElement => {
                  const [canSubmit, isSubmitting, isMutating, isFormSubmitted] = tuple as [boolean, boolean, boolean, boolean];
                  console.log('[GitHubTokenPopup] Button state:', { canSubmit, isSubmitting, isMutating, isFormSubmitted });
                  
                  return (
                    <Button 
                      type="submit" 
                      disabled={!canSubmit || isSubmitting || isMutating || isFormSubmitted}
                      className="w-full"
                    >
                      {isSubmitting || isMutating ? 'Submitting...' : isUpdate ? 'Update Token' : 'Submit Token'}
                    </Button>
                  );
                }}
              </form.Subscribe>
            </div>
          </form>
          
          <div className="text-xs text-center text-muted-foreground mt-2">
            <p>
              To create a PAT token, go to GitHub → Settings → Developer settings → Personal access tokens.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 