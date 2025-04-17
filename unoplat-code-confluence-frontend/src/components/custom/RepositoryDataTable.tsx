// File: RepositoryDataTable.tsx
"use client";

// Import necessary React hooks.
import  { useState, useEffect, forwardRef, useImperativeHandle, useMemo } from "react";
// Import useQuery from TanStack Query.
import { useQuery, useQueryClient } from '@tanstack/react-query';
// Import useRouter from TanStack Router.
// import { useRouter } from '@tanstack/react-router';

// Import the Dice UI DataTable component which is built on TanStack Table.
import { DataTable } from '../data-table';
// Import the custom hook that binds table state with router-based URL parameters.
import { useDataTableWithRouter } from '@/hooks/use-data-table-with-router';
// Import the column definitions for this repository table.
import { getRepositoryDataTableColumns } from "./repository-data-table-columns";

// Import the API function to fetch repository data along with type definitions.
import { fetchGitHubRepositories, type PaginatedResponse } from "../../lib/api";
import type { GitHubRepoSummary } from "../../types";
import { Route as OnboardingRoute } from "../../routes/_app.onboarding";
import { DataTableToolbar } from "../data-table-toolbar";

// Import the repository configuration dialog
import { RepositoryConfigDialog, type RepositoryConfig } from "./RepositoryConfigDialog";

// Define the ref interface so parent components can, for example, retrieve selected row names.
export interface RepositoryDataTableRef {
  getSelectedRowNames: () => string[];
}

export interface RowAction<T> {
  row: import('@tanstack/react-table').Row<T>;
  variant: string;
}

// Main component implementation using forwardRef so methods can be exposed.
export const RepositoryDataTable = forwardRef<RepositoryDataTableRef, { tokenStatus: boolean }>(
  function RepositoryDataTableFn({ tokenStatus }, ref) {
    const queryClient = useQueryClient();
    const { pageIndex, perPage, filterValues } = OnboardingRoute.useSearch();

    // 1️⃣ Track the current row action in state
    const [rowAction, setRowAction] = useState<RowAction<GitHubRepoSummary> | null>(null);
    const [repositoryConfigs, setRepositoryConfigs] = useState<Record<string, RepositoryConfig>>({});

    // Manage an array of pagination cursors. The initial cursor is undefined.
    const [cursors, setCursors] = useState<(string | undefined)[]>([undefined]);

    // Use TanStack Query to fetch repository data.
    const { data: repoData, isFetching } = useQuery<PaginatedResponse<GitHubRepoSummary>>({
      queryKey: ['repositories', pageIndex, perPage, filterValues, cursors[pageIndex - 1]],
      queryFn: () => fetchGitHubRepositories(pageIndex, perPage, filterValues, cursors[pageIndex - 1]),
      enabled: tokenStatus,
    });

    useEffect(() => {
      if (repoData?.next_cursor) {
        setCursors(prev => {
          const newCursors = [...prev];
          if (pageIndex >= newCursors.length) {
            newCursors.push(repoData.next_cursor);
          } else {
            newCursors[pageIndex] = repoData.next_cursor;
          }
          return newCursors;
        });
      }
    }, [repoData, pageIndex]);

    // 2️⃣ Build columns with the setter
    const columns = useMemo(() => {
      return getRepositoryDataTableColumns({ setRowAction });
    }, [setRowAction]);

    // 3️⃣ Initialize DiceUI DataTable
    const { table } = useDataTableWithRouter({
      data: repoData?.items || [],
      columns,
      pageCount: repoData?.has_next ? -1 : pageIndex,
      initialState: {
        pagination: {
          pageIndex: pageIndex - 1,
          pageSize: perPage,
        },
      },
      getRowId: (row: GitHubRepoSummary): string => row.name,
    });

    // Prefetch the next page when getting close to it
    useEffect(() => {
      if (repoData?.has_next && repoData?.next_cursor && tokenStatus) {
        const nextPageIndex = pageIndex + 1;
        const nextPageQueryKey = ['repositories', nextPageIndex, perPage, filterValues, repoData.next_cursor];
        queryClient.prefetchQuery({
          queryKey: nextPageQueryKey,
          queryFn: () => fetchGitHubRepositories(nextPageIndex, perPage, filterValues, repoData.next_cursor),
        });
      }
    }, [repoData, pageIndex, perPage, filterValues, queryClient, tokenStatus, cursors]);

    // Handle saving repository configuration
    function handleSaveConfig(config: RepositoryConfig): void {
      setRepositoryConfigs(prev => ({
        ...prev,
        [config.repositoryName]: config,
      }));
      setRowAction(null);
    }

    // Expose a method via the ref for compatibility (returns empty array, as no selection)
    useImperativeHandle(ref, () => ({
      getSelectedRowNames: (): string[] => [],
    }), []);

    // 4️⃣ Render DataTable and dialog
    return (
      <>
        <DataTable 
          table={table} 
          actionBar={null}
          isLoading={isFetching}
        >
          <DataTableToolbar table={table} />
        </DataTable>

        {/* Repository Configuration Dialog for per-row ingest */}
        {rowAction?.variant === 'ingest' && (
          <RepositoryConfigDialog
            repositoryName={rowAction.row.original.name}
            isOpen={true}
            onOpenChange={(open: boolean) => {
              if (!open) {
                setRowAction(null);
              }
            }}
            onSave={handleSaveConfig}
            existingConfig={repositoryConfigs[rowAction.row.original.name]}
            repositoryGitUrl={rowAction.row.original.git_url}
            repositoryOwnerName={rowAction.row.original.owner_name}
          />
        )}
      </>
    );
  }
);

RepositoryDataTable.displayName = "RepositoryDataTable";