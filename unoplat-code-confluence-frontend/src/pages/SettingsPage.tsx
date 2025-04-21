import React, { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import GitHubTokenPopup from '../components/custom/GitHubTokenPopup';
import { Card, CardContent } from '../components/ui/card';
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

export default function SettingsPage(): React.ReactElement {
  console.log('[SettingsPage] Rendering SettingsPage component');
  
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  console.log('[SettingsPage] State:', { showTokenPopup, showDeleteDialog, isDeleting });
  
  const handleDeleteToken = async (): Promise<void> => {
    console.log('[SettingsPage] Starting token deletion');
    try {
      setIsDeleting(true);
      console.log('[SettingsPage] Calling deleteGitHubToken API');
      await deleteGitHubToken();
      
      setShowDeleteDialog(false);
      console.log('[SettingsPage] Token deleted successfully, invalidating queries');
      
      // Invalidate and refetch the flag status
      await queryClient.invalidateQueries({ queryKey: ['flags', 'isTokenSubmitted'] });
      console.log('[SettingsPage] Queries invalidated');
      
      toast.success("Your GitHub token has been successfully removed");
    } catch (error) {
      console.error('[SettingsPage] Error deleting token:', error);
      toast.error(error instanceof Error ? error.message : "Failed to delete token");
    } finally {
      setIsDeleting(false);
    }
  };
  
  return (
    <div className="space-y-6 px-2 sm:px-6">
      <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
      <div className="flex flex-col gap-6">
        <Card className="shadow-sm max-w-4xl mx-auto">
          <CardContent className="w-full space-y-6 pt-6">
            <div className="space-y-2 pt-4 border-t">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <h3 className="text-lg font-medium">GitHub Authentication</h3>
                  <p className="text-sm text-muted-foreground">
                    Update GitHub Personal Access Token.
                  </p>
                </div>
                <div className="flex items-center gap-2 sm:self-start">
                  <Button 
                    variant="outline" 
                    onClick={(): void => {
                      console.log('[SettingsPage] Opening token management popup');
                      setShowTokenPopup(true);
                    }}
                    className="flex items-center gap-2"
                  >
                    <Github className="h-4 w-4" />
                    <span>Manage Token</span>
                  </Button>
                  <Button 
                    variant="destructive" 
                    size="icon"
                    onClick={(): void => {
                      console.log('[SettingsPage] Opening delete token confirmation dialog');
                      setShowDeleteDialog(true);
                    }}
                    title="Delete GitHub Token"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        {/* Add more Card sections here if needed for future settings */}
      </div>
      {/* GitHub Token Popup */}
      <GitHubTokenPopup 
        open={showTokenPopup} 
        onClose={(): void => {
          console.log('[SettingsPage] Token popup closed');
          setShowTokenPopup(false);
        }}
        isUpdate={true}
        onSuccess={(): void => {
          console.log('[SettingsPage] Token updated successfully');
          toast.success("Token updated successfully!", {
            description: "Success",
          });
        }}
      />
      {/* Delete Token Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={(isOpen: boolean): void => {
        console.log('[SettingsPage] Delete dialog change:', isOpen);
        setShowDeleteDialog(isOpen);
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
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={(): void => {
                console.log('[SettingsPage] Delete token confirmed');
                handleDeleteToken();
              }}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}