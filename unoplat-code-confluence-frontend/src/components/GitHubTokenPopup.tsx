import React, { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from '@tanstack/react-form';
import { submitGitHubToken, ApiError } from '../lib/api';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Dialog, DialogContent, DialogTitle } from './ui/dialog';
import { Github } from 'lucide-react';

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
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  // State for error notification
  const [error, setError] = useState<ApiError | null>(null);

  // Mutation for submitting the PAT token
  const tokenMutation = useMutation({
    mutationFn: submitGitHubToken,
    onSuccess: async () => {
      // Clear any errors
      setError(null);
      
      try {
        // Invalidate and refetch the flag status
        await queryClient.invalidateQueries({ queryKey: ['flags', 'isTokenSubmitted'] });
        
        // Execute onSuccess callback if provided
        if (onSuccess) {
          onSuccess();
        } else {
          // Redirect to the repository selection page if not in update mode
          if (!isUpdate) {
            navigate({ to: '/onboarding' });
          }
        }
        
        // Close the dialog
        onClose();
      } catch (error) {
        console.error('Error refreshing flag status:', error);
      }
    },
    onError: (error: unknown) => {
      console.error('Error submitting token:', error);
      
      // Set error for displaying in UI
      if ((error as ApiError).message) {
        setError(error as ApiError);
      } else {
        setError({
          message: 'Failed to submit token. Please try again.',
          isAxiosError: false
        });
      }
    }
  });

  // Create a form using TanStack Form
  const form = useForm({
    defaultValues: {
      patToken: '',
    },
    onSubmit: async ({ value }): Promise<void> => {
      if (!value.patToken.trim()) {
        setError({
          message: 'Please enter a valid PAT token',
          isAxiosError: false
        });
        return;
      }
      tokenMutation.mutate(value.patToken);
    },
  });

  return (
    <Dialog open={open} onOpenChange={(isOpen: boolean): void => {
      if (!isOpen) onClose();
    }}>
      <DialogContent className="sm:max-w-md">
        <DialogTitle className="sr-only">GitHub Authentication</DialogTitle>
        <div className="flex flex-col gap-6 items-center p-2">
          <div className="flex items-center gap-2 text-center">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
              <Github className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-xl font-semibold">GitHub Authentication</h1>
          </div>
          
          {/* Error Alert */}
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
            onSubmit={(e): void => {
              e.preventDefault();
              e.stopPropagation();
              form.handleSubmit();
            }}
            className="w-full space-y-4"
          >
            <div className="grid w-full gap-2">
              <form.Field
                name="patToken"
                validators={{
                  onChange: ({ value }): string | undefined => 
                    !value.trim() ? 'A GitHub token is required' : undefined,
                }}
              >
                {(field): React.ReactElement => (
                  <div className="grid gap-1">
                    <Label htmlFor={field.name} className="text-sm font-medium">
                      GitHub Personal Access Token (PAT)
                    </Label>
                    <Input
                      type="password"
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e): void => field.handleChange(e.target.value)}
                      placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                      className="w-full"
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
                selector={(state) => [state.canSubmit, state.isSubmitting, tokenMutation.isPending]}
              >
                {([canSubmit, isSubmitting, isMutating]): React.ReactElement => (
                  <Button 
                    type="submit" 
                    disabled={!canSubmit || isSubmitting || isMutating}
                    className="w-full"
                  >
                    {isSubmitting || isMutating ? 'Submitting...' : isUpdate ? 'Update Token' : 'Submit Token'}
                  </Button>
                )}
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