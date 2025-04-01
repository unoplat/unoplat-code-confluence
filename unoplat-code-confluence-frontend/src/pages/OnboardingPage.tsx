import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  SortingState,
  PaginationState,
  RowSelectionState,
} from '@tanstack/react-table';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { fetchGitHubRepositories, submitRepositories, ApiError } from '../lib/api';
import { useToast } from '../components/ui/use-toast';
import { RepositoryTable } from '../components/RepositoryTable';

export default function OnboardingPage(): React.ReactElement {
  const { toast } = useToast();
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState<string>('');
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});

  // Query for repositories
  const {
    data: repositories = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['repositories'],
    queryFn: fetchGitHubRepositories,
    enabled: true, // Fetch automatically when component mounts
  });

  // Get appropriate error message based on error details
  const getErrorMessage = (): { title: string; message: string; action: string } => {
    // Safely cast error to ApiError, ensuring it's actually an ApiError type
    if (!error) {
      return {
        title: 'Unknown Error',
        message: 'An unexpected error occurred.',
        action: 'Please try refreshing the page.'
      };
    }

    // Check if error is an ApiError by checking for the isAxiosError property
    const apiError = error as unknown as ApiError;
    const isApiError = apiError && 'isAxiosError' in apiError;
    
    // If it's not an ApiError, provide a default error message
    if (!isApiError) {
      return {
        title: 'Error Fetching Repositories',
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        action: 'Please try refreshing the page.'
      };
    }
    
    const statusCode = apiError.statusCode;
    const errorMessage = apiError.message || 'Unknown error occurred';
    
    // Default error info
    let title = 'Error Fetching Repositories';
    let message = 'We encountered an issue while trying to fetch your repositories.';
    let action = 'Please try refreshing the page.';
    
    // Handle specific error cases
    if (statusCode === 404) {
      title = 'GitHub Credentials Missing';
      message = 'We couldn\'t find your GitHub credentials in our system.';
      action = 'Please set up your GitHub token first.';
    } else if (statusCode === 401 || (errorMessage && errorMessage.includes('token'))) {
      title = 'Authentication Error';
      message = 'Your GitHub token may have expired or doesn\'t have the necessary permissions.';
      action = 'Please update your GitHub toke from settings page with appropriate permissions.';
    } else if (statusCode === 500) {
      if (errorMessage.includes('decryption')) {
        title = 'Token Decryption Error';
        message = 'We had trouble decrypting your GitHub token.';
        action = 'Please try setting up your token again.';
      } else if (errorMessage.includes('GitHub API error')) {
        title = 'GitHub API Error';
        message = 'GitHub API returned an error while fetching your repositories.';
        action = 'Please check your GitHub account status and try again later.';
      } else if (errorMessage.includes('Database error')) {
        title = 'System Error';
        message = 'We encountered a database issue while accessing your credentials.';
        action = 'Please try again later. If the problem persists, contact support.';
      }
    }
    
    return { title, message, action };
  };

  // Function to handle submitting selected repositories
  const handleSubmitSelections = async (): Promise<void> => {
    try {
      const selectedRepoNames = Object.keys(rowSelection)
        .map((idx) => repositories[parseInt(idx)]?.name)
        .filter(Boolean);

      if (selectedRepoNames.length === 0) {
        toast({
          variant: "destructive",
          title: "Selection Required",
          description: "Please select at least one repository to continue."
        });
        return;
      }

      await submitRepositories(selectedRepoNames);
      
      toast({
        title: "Success",
        description: "Repositories submitted for ingestion successfully!"
      });
      
      // Navigate to dashboard
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Error submitting repositories:', error);
      toast({
        variant: "destructive",
        title: "Submission Failed",
        description: "Failed to submit repositories for ingestion."
      });
    }
  };

  // Route to token setup page
  const goToTokenSetup = (): void => {
    window.location.href = '/setup';
  };

  // Function to safely check if an error is an ApiError with the specified status
  const isApiErrorWithStatus = (statusCode: number): boolean => {
    if (!error) return false;
    const apiError = error as unknown as ApiError;
    return 'isAxiosError' in apiError && apiError.statusCode === statusCode;
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold tracking-tight mb-6">GitHub Repository Selection</h1>

      {/* Repository List */}
      <Card>
        <CardHeader>
          <CardTitle>GitHub Repositories</CardTitle>
          <CardDescription>
            Select repositories to ingest into our system.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Loading and Error States */}
          {isLoading && (
            <div className="flex justify-center py-6">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}

          {error && (
            <div className="bg-destructive/10 border-l-4 border-destructive p-4 mb-4 rounded">
              <div className="flex flex-col">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-destructive">
                    {getErrorMessage().title}
                  </h3>
                  <p className="text-sm text-destructive/90 mt-1">
                    {getErrorMessage().message}
                  </p>
                  <p className="text-sm text-destructive/80 mt-2">
                    {getErrorMessage().action}
                  </p>
                  <div className="mt-3 flex flex-row gap-2">
                    <Button
                      variant="outline"
                      onClick={() => refetch()}
                      size="sm"
                    >
                      Try Again
                    </Button>
                    {isApiErrorWithStatus(404) && (
                      <Button
                        variant="default"
                        onClick={goToTokenSetup}
                        size="sm"
                      >
                        Set Up GitHub Token
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {!isLoading && !error && repositories.length > 0 && (
            <>
              {/* Use the RepositoryTable component */}
              <RepositoryTable
                repositories={repositories}
                rowSelection={rowSelection}
                onRowSelectionChange={setRowSelection}
                globalFilter={globalFilter}
                onGlobalFilterChange={setGlobalFilter}
                pagination={pagination}
                onPaginationChange={setPagination}
                sorting={sorting}
                onSortingChange={setSorting}
              />

              {/* Submit Button */}
              <div className="mt-6 flex gap-2">
                <Button
                  onClick={handleSubmitSelections}
                  disabled={Object.keys(rowSelection).length === 0}
                >
                  Submit Selected Repositories
                </Button>
              </div>
            </>
          )}

          {!isLoading && !error && repositories.length === 0 && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
              <div className="flex">
                <div className="ml-3">
                  <p className="text-sm text-amber-700">
                    No repositories found. This could be because your GitHub token doesn't have the necessary permissions.
                  </p>
                  <div className="mt-2 flex gap-2">
                    <Button
                      variant="ghost"
                      onClick={() => refetch()}
                      size="sm"
                    >
                      Try refreshing
                    </Button>
                    <Button
                      variant="outline"
                      onClick={goToTokenSetup}
                      size="sm"
                    >
                      Update GitHub Token
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 