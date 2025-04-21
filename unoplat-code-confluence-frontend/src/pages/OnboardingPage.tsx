import React, { useRef, useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { AlertCircle } from 'lucide-react';
import { RepositoryDataTable, type RepositoryDataTableRef } from '../components/custom/RepositoryDataTable';
import GitHubTokenPopup from '../components/custom/GitHubTokenPopup';
import { useAuthStore } from '@/stores/useAuthStore';
import { useAuthData } from '@/hooks/use-auth-data';

export default function OnboardingPage(): React.ReactElement {
  console.log('[OnboardingPage] Rendering OnboardingPage component');
  
  const queryClient = useQueryClient();
  const dataTableRef = useRef<RepositoryDataTableRef>(null);
  
  // Use useAuthData hook to fetch token status and user data
  const { tokenQuery } = useAuthData();
  // Local control for token popup open/close
  const [isPopupOpen, setIsPopupOpen] = useState<boolean>(false);
  // Track whether we've auto-opened already to avoid re-opening on manual close
  const autoOpenRef = useRef<boolean>(false);
  // Auto-open the popup once when token status is known and no token exists
  useEffect(() => {
    if (
      !autoOpenRef.current &&
      tokenQuery.isSuccess &&
      !tokenQuery.data?.status &&
      tokenQuery.data.errorCode !== 503
    ) {
      autoOpenRef.current = true;
      setIsPopupOpen(true);
    }
  }, [tokenQuery.isSuccess, tokenQuery.data?.status, tokenQuery.data?.errorCode]);
  const showTokenPopup = isPopupOpen;
  
  console.log('[OnboardingPage] State: showTokenPopup =', showTokenPopup);

  // Use Zustand store for auth state
  const tokenStatus = useAuthStore((state) => state.tokenStatus);

  const handleTokenSuccess = async (): Promise<void> => {
    console.log('[OnboardingPage] Token submitted successfully');
    
    console.log('[OnboardingPage] Invalidating repositories query after token submission');
    // Since token status is now handled by Zustand, we only need to invalidate repositories
    await queryClient.invalidateQueries({ queryKey: ['repositories'] });
  };

  console.log('[OnboardingPage] Rendering UI with tokenStatus:', tokenStatus?.status);
  return (
    <div className="container py-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">GitHub Repositories</CardTitle>
          <CardDescription className="text-base font-normal">
          Connect your GitHub repositories to Unoplat Code Confluence to unlock deeper code insights. Browse the repositories below, click "Ingest Repo" in the row actions, fill in the required details, and submit to begin ingestion.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {tokenStatus && !tokenStatus.status && !showTokenPopup && tokenStatus.errorCode !== 503 && (
            <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-5 w-5 text-amber-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h3 className="text-xl font-semibold text-amber-800">GitHub Token Required</h3>
                  <div className="mt-2 text-sm text-amber-700">
                    <p className="text-base font-normal">You need to provide a GitHub token to access your repositories.</p>
                    <div className="mt-3">
                      <Button 
                        variant="outline" 
                        onClick={() => {
                          console.log('[OnboardingPage] "Set up GitHub Token" button clicked');
                          setIsPopupOpen(true);
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
                  <h3 className="text-xl font-semibold text-red-800">Connection Error</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p className="text-base font-normal">Could not connect to the server. Please refresh the page.</p>
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
      </Card>

      <GitHubTokenPopup 
        open={showTokenPopup}
        onClose={() => {
          console.log('[OnboardingPage] Token popup closed');
          setIsPopupOpen(false);
        }}
        onSuccess={async () => {
          await handleTokenSuccess();
          setIsPopupOpen(false);
        }}
      />
    </div>
  );
}