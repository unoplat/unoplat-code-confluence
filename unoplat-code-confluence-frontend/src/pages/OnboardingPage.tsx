import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { AlertCircle } from 'lucide-react';
import { getFlagStatus } from '../lib/api';
import { RepositoryDataTable, type RepositoryDataTableRef } from '../components/custom/RepositoryDataTable';
import GitHubTokenPopup from '../components/GitHubTokenPopup';
import { FlagResponse } from '../types';

export default function OnboardingPage(): React.ReactElement {
  console.log('[OnboardingPage] Rendering OnboardingPage component');
  
  const queryClient = useQueryClient();
  const dataTableRef = useRef<RepositoryDataTableRef>(null);
  
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  
  
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
  
  // Row-selection and submission functionality removed as it's no longer supported

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
      <h1 className="text-4xl font-extrabold tracking-tight mb-6 text-primary">Select GitHub Repositories for Ingestion</h1>

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