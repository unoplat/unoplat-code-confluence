import React, { useState } from 'react';
import { useQueryClient, useMutation } from '@tanstack/react-query';
import GitHubTokenPopup from '../components/custom/GitHubTokenPopup';
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Github, Trash2 } from 'lucide-react';
import { deleteGitHubToken } from '../lib/api';
import { useToast } from '../components/ui/use-toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../components/ui/alert-dialog';
import { useAuthData } from '@/hooks/use-auth-data';
import type { ApiResponse } from '../lib/api'; // Import ApiResponse type

export default function SettingsPage(): React.ReactElement {
  // console.log('[SettingsPage] Rendering SettingsPage component');
  
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false);
  // const [isDeleting, setIsDeleting] = useState<boolean>(false); // Removed isDeleting state
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { tokenQuery } = useAuthData(); // Use the auth data hook

  // console.log('[SettingsPage] State:', { showTokenPopup, showDeleteDialog });
  // console.log('[SettingsPage] Auth Data:', { tokenQuery });

  // Define the mutation for deleting the token
  const deleteMutation = useMutation<ApiResponse, Error>({
    mutationFn: deleteGitHubToken, // Use mutationFn instead of passing directly
    onSuccess: async (data: ApiResponse) => {
      // console.log('[SettingsPage] Token deleted successfully via mutation, invalidating queries', data);
      setShowDeleteDialog(false);
      
      // Invalidate and refetch the flag status
      await queryClient.invalidateQueries({ queryKey: ['flags', 'isTokenSubmitted'] });
      // console.log('[SettingsPage] Queries invalidated via mutation');
      
      toast.success(data.message || "Your GitHub token has been successfully removed");
    },
    onError: (error: Error) => {
      console.error('[SettingsPage] Error deleting token via mutation:', error);
      toast.error(error.message || "Failed to delete token");
    },
    // Optional: Reset mutation state when dialog closes
    // onSettled: () => {
    //   if (!showDeleteDialog) {
    //     deleteMutation.reset();
    //   }
    // }
  });
  
  // Removed handleDeleteToken function

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-6">
        <Card className="shadow-md border-border bg-card">
          <CardHeader className="max-w-4xl mx-auto px-8 py-6">
            <div className="flex items-center justify-between space-x-6">
              <div className="space-y-2">
                <CardTitle className="text-xl font-semibold tracking-tight">GitHub Authentication</CardTitle>
                <CardDescription className="text-base text-muted-foreground leading-relaxed">
                  {tokenQuery.data?.status ? 'Update or remove your GitHub Personal Access Token.' : 'Connect your GitHub account to access repositories.'}
                </CardDescription>
              </div>
              <div className="flex items-center gap-3">
                <Button
                  variant="outline"
                  size="default"
                  onClick={(): void => {
                    // console.log('[SettingsPage] Opening token management popup');
                    setShowTokenPopup(true);
                  }}
                  className="flex items-center gap-2 min-w-[120px]"
                  // Optionally disable if token is loading or there's an error initially fetching it
                  // disabled={tokenQuery.isLoading || tokenQuery.isError} 
                >
                  <Github className="h-4 w-4" />
                  <span>{tokenQuery.data?.status ? 'Manage Token' : 'Add Token'}</span>
                </Button>
                {tokenQuery.data?.status && ( // Only show delete if a token exists
                  <Button
                    variant="destructive"
                    size="icon"
                    onClick={(): void => {
                      // console.log('[SettingsPage] Opening delete token confirmation dialog');
                      setShowDeleteDialog(true);
                    }}
                    title="Delete GitHub Token"
                    disabled={deleteMutation.isPending || tokenQuery.isLoading} // Use isPending instead of isLoading
                    className="h-10 w-10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
        </Card>
        {/* Add more Card sections here if needed for future settings */}
      </div>
      {/* GitHub Token Popup */}
      <GitHubTokenPopup 
        open={showTokenPopup} 
        onClose={(): void => {
          // console.log('[SettingsPage] Token popup closed');
          setShowTokenPopup(false);
        }}
        isUpdate={!!tokenQuery.data?.status} // Pass based on token status
        onSuccess={(): void => {
          // console.log('[SettingsPage] Token updated successfully');
          // Invalidation is handled by the popup/API call itself or its success callback if needed
          toast.success(tokenQuery.data?.status ? "Token updated successfully!" : "Token added successfully!", {
            description: "Success",
          });
        }}
      />
      {/* Delete Token Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={(isOpen: boolean): void => {
        // console.log('[SettingsPage] Delete dialog change:', isOpen);
        setShowDeleteDialog(isOpen);
        if (!isOpen) {
          // console.log('[SettingsPage] Resetting delete mutation state on dialog close');
          deleteMutation.reset(); // Reset mutation state if dialog is closed
        }
      }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete GitHub Token</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete your GitHub Personal Access Token? 
              This action will remove access to your GitHub repositories and cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMutation.isPending}>Cancel</AlertDialogCancel> {/* Use isPending */}
            <AlertDialogAction 
              onClick={(): void => {
                // console.log('[SettingsPage] Delete token confirmed, calling mutation');
                deleteMutation.mutate(); // Trigger the mutation
              }}
              disabled={deleteMutation.isPending} // Use isPending
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"} {/* Use isPending */}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}