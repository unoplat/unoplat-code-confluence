import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { AlertCircle } from 'lucide-react';
import { 
  submitRepositories, 
  getFlagStatus, 
} from '../lib/api';
import { useToast } from '../components/ui/use-toast';
import { RepositoryDataTable, type RepositoryDataTableRef } from '../components/custom/RepositoryDataTable';
import GitHubTokenPopup from '../components/GitHubTokenPopup';
import { FlagResponse } from '../types';

export default function OnboardingPage(): React.ReactElement {
  console.log('[OnboardingPage] Rendering OnboardingPage component');
  
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const dataTableRef = useRef<RepositoryDataTableRef>(null);
  
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  const [hasSelection, setHasSelection] = useState<boolean>(false);
  
  console.log('[OnboardingPage] State: showTokenPopup =', showTokenPopup);

  const { data: tokenStatus } = useQuery<FlagResponse>({
    queryKey: ['flags', 'isTokenSubmitted'],
    queryFn: () => {
      
      return getFlagStatus('isTokenSubmitted');
    },
  });

  useEffect(() => {
    console.log('[OnboardingPage] Token status updated:', tokenStatus);
    if (tokenStatus && !tokenStatus.status) {
      console.log('[OnboardingPage] Token not submitted, showing token popup');
      setShowTokenPopup(true);
    }
  }, [tokenStatus]);
  
  // Set up an interval to check selection status
  useEffect(() => {
    if (!tokenStatus?.status) return;
    
    const checkSelection = (): void => {
      const count = dataTableRef.current?.getSelectedRowNames().length ?? 0;
      setHasSelection(count > 0);
    };
    
    // Check initially
    checkSelection();
    
    // Set up interval to periodically check
    const intervalId = setInterval(checkSelection, 300);
    
    return () => clearInterval(intervalId);
  }, [tokenStatus?.status]);

  const handleSubmitSelections = async (): Promise<void> => {
    try {
      const selectedRepoNames = dataTableRef.current?.getSelectedRowNames() ?? [];
      console.log('[OnboardingPage] Submitting repositories:', selectedRepoNames);
      
      if (selectedRepoNames.length === 0) {
        console.log('[OnboardingPage] No repositories selected, showing error toast');
        toast({
          variant: "destructive",
          title: "Selection Required",
          description: "Please select at least one repository to continue."
        });
        return;
      }
      
      console.log('[OnboardingPage] Calling submitRepositories API');
      await submitRepositories(selectedRepoNames);
      
      console.log('[OnboardingPage] Repositories submitted successfully, showing success toast');
      toast({
        title: "Success",
        description: "Repositories submitted for ingestion successfully!"
      });
      
      console.log('[OnboardingPage] Navigating to dashboard');
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('[OnboardingPage] Error submitting repositories:', error);
      toast({
        variant: "destructive",
        title: "Submission Failed",
        description: "Failed to submit repositories for ingestion."
      });
    }
  };

  const handleTokenSuccess = async (): Promise<void> => {
    console.log('[OnboardingPage] Token submitted successfully, hiding popup');
    setShowTokenPopup(false);
    
    console.log('[OnboardingPage] Invalidating queries after token submission');
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['flags', 'isTokenSubmitted'] }),
      queryClient.invalidateQueries({ queryKey: ['repositories'] })
    ]);
  };

  console.log('[OnboardingPage] Rendering UI with tokenStatus:', tokenStatus?.status);
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold tracking-tight mb-6">Select GitHub Repositories for Ingestion</h1>

      <Card>
        <CardHeader>
          <CardTitle>GitHub Repositories</CardTitle>
          <CardDescription>
            Connect your GitHub repositories to Unoplat Code Confluence for deeper code insights. Scroll through your available repositories below and select the ones you want to ingest.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {(!tokenStatus?.status && !showTokenPopup && tokenStatus?.errorCode !== 503) && (
            <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-5 w-5 text-amber-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-amber-800">GitHub Token Required</h3>
                  <div className="mt-2 text-sm text-amber-700">
                    <p>You need to provide a GitHub token to access your repositories.</p>
                    <div className="mt-3">
                      <Button 
                        variant="outline" 
                        onClick={() => {
                          console.log('[OnboardingPage] "Set up GitHub Token" button clicked');
                          setShowTokenPopup(true);
                        }} 
                        size="sm"
                      >
                        Set up GitHub Token
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {tokenStatus?.errorCode === 503 && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-5 w-5 text-red-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Connection Error</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>Could not connect to the server. Please refresh the page.</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {tokenStatus?.status && (
            <RepositoryDataTable 
              ref={dataTableRef}
              tokenStatus={tokenStatus.status}
            />
          )}
        </CardContent>
        
        {tokenStatus?.status && (
          <CardFooter className="flex justify-between border-t bg-muted/50 px-6 py-4">
            <div className="text-sm text-muted-foreground">
              {hasSelection ? 'Ready to submit your selection' : 'Select repositories to continue'}
            </div>
            <Button 
              onClick={() => {
                console.log('[OnboardingPage] "Submit Selected Repositories" button clicked');
                handleSubmitSelections();
              }}
              disabled={!hasSelection}
            >
              Submit
            </Button>
          </CardFooter>
        )}
      </Card>

      <GitHubTokenPopup 
        open={showTokenPopup} 
        onClose={() => {
          console.log('[OnboardingPage] Token popup closed');
          setShowTokenPopup(false);
        }} 
        onSuccess={handleTokenSuccess} 
      />
    </div>
  );
}