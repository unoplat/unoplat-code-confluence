// File: RepositoryDataTable.tsx
"use client";

// Import necessary React hooks.
import  { useState, useEffect, forwardRef, useImperativeHandle, useMemo } from "react";
// Import useQuery from TanStack Query.
import { useQuery, useQueryClient, keepPreviousData } from '@tanstack/react-query';
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
import { RepositoryConfigDialog } from "./RepositoryConfigDialog";

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
    // Manage an array of pagination cursors. The initial cursor is undefined.
    const [cursors, setCursors] = useState<(string | undefined)[]>([undefined]);

    // Use TanStack Query to fetch repository data.
    const {
      data: repoData,
      isFetching,
      isPlaceholderData,
    } = useQuery<PaginatedResponse<GitHubRepoSummary>>({
      queryKey: [
        'repositories',
        pageIndex,
        perPage,
        filterValues,
        cursors[pageIndex - 1],
      ],
      queryFn: () =>
        fetchGitHubRepositories(
          pageIndex,
          perPage,
          filterValues,
          cursors[pageIndex - 1],
        ),
      enabled: tokenStatus,
      placeholderData: keepPreviousData,
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnMount: false,
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

    // Prefetch two pages ahead
    useEffect(() => {
      if (!tokenStatus || !repoData?.has_next || !repoData.next_cursor) return;

      // Prefetch page+1
      const cursor1: string = repoData.next_cursor;
      const pageToPrefetch1: number = pageIndex + 1;
      queryClient.prefetchQuery({
        queryKey: ['repositories', pageToPrefetch1, perPage, filterValues, cursor1],
        queryFn: () =>
          fetchGitHubRepositories(
            pageToPrefetch1,
            perPage,
            filterValues,
            cursor1,
          ),
      });

      // Also fetch page+1 data to obtain its cursor, then prefetch page+2
      fetchGitHubRepositories(
        pageToPrefetch1,
        perPage,
        filterValues,
        cursor1,
      )
        .then((nextPageData: PaginatedResponse<GitHubRepoSummary>) => {
          if (nextPageData.next_cursor) {
            const cursor2: string = nextPageData.next_cursor;
            const pageToPrefetch2: number = pageIndex + 2;
            queryClient.prefetchQuery({
              queryKey: ['repositories', pageToPrefetch2, perPage, filterValues, cursor2],
              queryFn: () =>
                fetchGitHubRepositories(
                  pageToPrefetch2,
                  perPage,
                  filterValues,
                  cursor2,
                ),
            });
          }
        })
        .catch(() => {
          // ignore prefetch errors
        });
    }, [repoData, pageIndex, perPage, filterValues, queryClient, tokenStatus]);


    // Expose a method via the ref for compatibility (returns empty array, as no selection)
    useImperativeHandle(ref, () => ({
      getSelectedRowNames: (): string[] => [],
    }), []);

    // 4️⃣ Render DataTable and dialog
    return (
      <>
        <div className="w-full">
          <DataTable
            table={table}
            actionBar={null}
            isLoading={isFetching && !isPlaceholderData}
          >
            <DataTableToolbar table={table} />
          </DataTable>
        </div>

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
            repositoryGitUrl={rowAction.row.original.git_url}
            repositoryOwnerName={rowAction.row.original.owner_name}
          />
        )}
      </>
    );
  }
);

RepositoryDataTable.displayName = "RepositoryDataTable";