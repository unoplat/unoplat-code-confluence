import React, { useState } from 'react';
import { Link } from '@tanstack/react-router';
import GitHubTokenPopup from '../components/GitHubTokenPopup';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Github, ExternalLink, Trash2 } from 'lucide-react';
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
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const { toast } = useToast();
  
  const handleDeleteToken = async (): Promise<void> => {
    try {
      setIsDeleting(true);
      await deleteGitHubToken();
      setShowDeleteDialog(false);
      toast({
        title: "Success",
        description: "Your GitHub token has been successfully removed",
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete token",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
    }
  };
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
      
      <Card>
        <CardContent className="space-y-6 pt-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">GitHub Repositories</h3>
                <p className="text-sm text-muted-foreground">
                  Add or manage GitHub repositories for ingestion.
                </p>
              </div>
              <Button asChild variant="outline">
                <Link to="/onboarding" className="flex items-center gap-2">
                  <span>Go to Onboarding</span>
                  <ExternalLink className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
          
          <div className="space-y-2 pt-2 border-t">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">GitHub Authentication</h3>
                <p className="text-sm text-muted-foreground">
                  Update or change your GitHub Personal Access Token.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => setShowTokenPopup(true)}
                  className="flex items-center gap-2"
                >
                  <Github className="h-4 w-4" />
                  <span>Manage Token</span>
                </Button>
                <Button 
                  variant="destructive" 
                  size="icon"
                  onClick={() => setShowDeleteDialog(true)}
                  title="Delete GitHub Token"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* GitHub Token Popup */}
      <GitHubTokenPopup 
        open={showTokenPopup} 
        onClose={() => setShowTokenPopup(false)}
        isUpdate={true}
        onSuccess={() => {
          toast({
            title: "Success",
            description: "Token updated successfully!",
            variant: "default",
          });
        }}
      />

      {/* Delete Token Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
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
              onClick={handleDeleteToken}
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