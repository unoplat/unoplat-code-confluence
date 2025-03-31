import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  SortingState,
  PaginationState,
  RowSelectionState,
} from '@tanstack/react-table';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { fetchGitHubRepositories, submitRepositories } from '../lib/api';
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
              <div className="flex">
                <div className="ml-3">
                  <p className="text-sm text-destructive">
                    Failed to fetch repositories. Please try refreshing the page.
                  </p>
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
                  <Button
                    variant="ghost"
                    onClick={() => refetch()}
                    className="mt-2"
                  >
                    Try refreshing
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 