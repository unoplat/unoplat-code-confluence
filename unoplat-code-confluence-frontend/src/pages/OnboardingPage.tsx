import React, { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  SortingState,
  PaginationState,
  RowSelectionState,
} from '@tanstack/react-table';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { AlertCircle } from 'lucide-react';
import { 
  fetchGitHubRepositories, 
  submitRepositories, 
  ApiError, 
  getFlagStatus, 
  FlagResponse, 
  PaginatedResponse 
} from '../lib/api';
import { GitHubRepoSummary } from '../types';
import { useToast } from '../components/ui/use-toast';
import { RepositoryDataTable } from '../components/RepositoryDataTable';
import GitHubTokenPopup from '../components/GitHubTokenPopup';
import { useRouter } from '@tanstack/react-router';
import type { OnChangeFn } from '@tanstack/react-table';

export default function OnboardingPage(): React.ReactElement {
  const { toast } = useToast();
  const router = useRouter();
  const urlSorting = (((router.state as any).search || {}) as { sorting?: SortingState }).sorting;
  const [sorting, setSorting] = useState<SortingState>(urlSorting || []);
  const urlPagination = (((router.state as any).search || {}) as { pagination?: PaginationState }).pagination;
  const [pagination, setPagination] = useState<PaginationState>(urlPagination || { pageIndex: 0, pageSize: 10 });
  const urlRowSelection = (((router.state as any).search || {}) as { rowSelection?: RowSelectionState }).rowSelection;
  const [rowSelection, setRowSelection] = useState<RowSelectionState>(urlRowSelection || {});
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  const [nextCursor, setNextCursor] = useState<string | undefined>(undefined);
  const [cursors, setCursors] = useState<Array<string | undefined>>([undefined]);
  const queryClient = useQueryClient();
  
  // Query for token status
  const { data: tokenStatus } = useQuery<FlagResponse>({
    queryKey: ['flags', 'isTokenSubmitted'],
    queryFn: () => getFlagStatus('isTokenSubmitted'),
  });

  useEffect(() => {
    if (tokenStatus && !tokenStatus.status) {
      setShowTokenPopup(true);
    }
  }, [tokenStatus]);
  
  // Update cursors when page changes
  useEffect(() => {
    // Only save cursor for the current page if we don't already have it
    if (pagination.pageIndex >= cursors.length - 1 && nextCursor) {
      setCursors(prev => [...prev, nextCursor]);
    }
  }, [nextCursor, pagination.pageIndex, cursors.length]);

  // Create empty data placeholder
  const emptyRepoData: PaginatedResponse<GitHubRepoSummary> = {
    items: [],
    per_page: pagination.pageSize,
    has_next: false,
    next_cursor: undefined
  };

  // Query for repositories, only enabled when token is present
  const {
    data: repoData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['repositories', pagination.pageIndex, pagination.pageSize, sorting, cursors[pagination.pageIndex]],
    queryFn: () => fetchGitHubRepositories(
      pagination.pageIndex + 1, 
      pagination.pageSize, 
      undefined, 
      cursors[pagination.pageIndex]
    ),
    enabled: tokenStatus?.status ?? false,
    placeholderData: tokenStatus?.status ? undefined : emptyRepoData,
  });

  // Update cursor on successful data fetch
  useEffect(() => {
    if (repoData?.next_cursor) {
      setNextCursor(repoData.next_cursor);
    }
  }, [repoData]);

  const repositoriesData: PaginatedResponse<GitHubRepoSummary> = repoData ?? emptyRepoData;

  const getErrorMessage = (): { title: string; message: string; action: string } => {
    if (!error) {
      return {
        title: 'Unknown Error',
        message: 'An unexpected error occurred.',
        action: 'Please try refreshing the page.'
      };
    }
    const apiError = error as unknown as ApiError;
    const isApiError = apiError && 'isAxiosError' in apiError;
    if (!isApiError) {
      return {
        title: 'Error Fetching Repositories',
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        action: 'Please try refreshing the page.'
      };
    }
    const statusCode = apiError.statusCode;
    const errorMessage = apiError.message || 'Unknown error occurred';
    let title = 'Error Fetching Repositories';
    let message = 'We encountered an issue while trying to fetch your repositories.';
    let action = 'Please try refreshing the page.';
    if (statusCode === 404) {
      title = 'GitHub Credentials Missing';
      message = 'We couldn\'t find your GitHub credentials in our system.';
      action = 'Please set up your GitHub token first.';
    } else if (statusCode === 401 || (errorMessage && errorMessage.includes('token'))) {
      title = 'Authentication Error';
      message = 'Your GitHub token may have expired or doesn\'t have the necessary permissions.';
      action = 'Please update your GitHub token from the settings page with appropriate permissions.';
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

  const handleSubmitSelections = async (): Promise<void> => {
    try {
      const selectedRepoNames = Object.keys(rowSelection)
        .map((idx) => repositoriesData.items[parseInt(idx)]?.name)
        .filter(Boolean) as string[];
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

  const handleTokenSuccess = async (): Promise<void> => {
    setShowTokenPopup(false);
    // Reset pagination and cursors when token is updated
    setPagination({ pageIndex: 0, pageSize: 10 });
    setCursors([undefined]);
    setNextCursor(undefined);
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['flags', 'isTokenSubmitted'] }),
      queryClient.invalidateQueries({ queryKey: ['repositories'] })
    ]);
  };

  const isApiErrorWithStatus = (statusCode: number): boolean => {
    if (!error) return false;
    const apiError = error as unknown as ApiError;
    return 'isAxiosError' in apiError && apiError.statusCode === statusCode;
  };

  const handleSortingChange: OnChangeFn<SortingState> = (updaterOrValue): SortingState => {
    const newValue = typeof updaterOrValue === 'function' ? updaterOrValue(sorting) : updaterOrValue;
    setSorting(newValue);
    const currentSearch = (router.state as any).search || {};
    router.navigate({ search: { ...currentSearch, sorting: newValue } });
    return newValue;
  };

  const handlePaginationChange: OnChangeFn<PaginationState> = (updaterOrValue): PaginationState => {
    const newValue = typeof updaterOrValue === 'function' ? updaterOrValue(pagination) : updaterOrValue;
    
    // Check if page size has changed
    const isPageSizeChanged = newValue.pageSize !== pagination.pageSize;
    
    // If page size changed, reset pagination state and cursors
    if (isPageSizeChanged) {
      // Reset cursors when page size changes
      setCursors([undefined]);
      setNextCursor(undefined);
      
      // Always go to first page when changing page size
      const resetValue = { ...newValue, pageIndex: 0 };
      setPagination(resetValue);
      
      // Invalidate queries to fetch with new page size
      queryClient.invalidateQueries({ queryKey: ['repositories'] });
      
      // Update URL
      const currentSearch = (router.state as any).search || {};
      router.navigate({ search: { ...currentSearch, pagination: resetValue } });
      
      return resetValue;
    } else {
      // Regular pagination change (page navigation)
      setPagination(newValue);
      const currentSearch = (router.state as any).search || {};
      router.navigate({ search: { ...currentSearch, pagination: newValue } });
      return newValue;
    }
  };

  const handleRowSelectionChange: OnChangeFn<RowSelectionState> = (updaterOrValue): RowSelectionState => {
    const newValue = typeof updaterOrValue === 'function' ? updaterOrValue(rowSelection) : updaterOrValue;
    setRowSelection(newValue);
    const currentSearch = (router.state as any).search || {};
    router.navigate({ search: { ...currentSearch, rowSelection: newValue } });
    return newValue;
  };

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
          {(!tokenStatus?.status && !showTokenPopup) && (
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
                      <Button variant="outline" onClick={() => setShowTokenPopup(true)} size="sm">
                        Set up GitHub Token
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {tokenStatus?.status && isLoading && (
            <div className="flex justify-center py-6">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}

          {tokenStatus?.status && error && (
            <div className="bg-destructive/10 border-l-4 border-destructive p-4 mb-4 rounded">
              <div className="flex flex-col">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-destructive">{getErrorMessage().title}</h3>
                  <p className="text-sm text-destructive/90 mt-1">{getErrorMessage().message}</p>
                  <p className="text-sm text-destructive/80 mt-2">{getErrorMessage().action}</p>
                  <div className="mt-3 flex flex-row gap-2">
                    <Button variant="outline" onClick={() => refetch()} size="sm">
                      Try Again
                    </Button>
                    {isApiErrorWithStatus(404) && (
                      <Button variant="default" onClick={() => setShowTokenPopup(true)} size="sm">
                        Set Up GitHub Token
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {tokenStatus?.status && !isLoading && !error && (
            <>
              {repositoriesData.items.length > 0 ? (
                <>
                  <RepositoryDataTable
                    repositories={repositoriesData.items}
                    rowSelection={rowSelection}
                    onRowSelectionChange={handleRowSelectionChange}
                    pagination={pagination}
                    onPaginationChange={handlePaginationChange}
                    sorting={sorting}
                    onSortingChange={handleSortingChange}
                    pageCount={repositoriesData.has_next ? pagination.pageIndex + 2 : pagination.pageIndex + 1}
                  />
                  <div className="mt-6 flex gap-2">
                    <Button onClick={handleSubmitSelections} disabled={Object.keys(rowSelection).length === 0}>
                      Submit Selected Repositories
                    </Button>
                  </div>
                </>
              ) : (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                  <div className="flex">
                    <div className="ml-3">
                      <p className="text-sm text-amber-700">
                        No repositories found. This could be because your GitHub token doesn't have the necessary permissions.
                      </p>
                      <div className="mt-2 flex gap-2">
                        <Button variant="ghost" onClick={() => refetch()} size="sm">
                          Try refreshing
                        </Button>
                        <Button variant="outline" onClick={() => setShowTokenPopup(true)} size="sm">
                          Update GitHub Token
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <GitHubTokenPopup open={showTokenPopup} onClose={() => setShowTokenPopup(false)} onSuccess={handleTokenSuccess} />
    </div>
  );
}