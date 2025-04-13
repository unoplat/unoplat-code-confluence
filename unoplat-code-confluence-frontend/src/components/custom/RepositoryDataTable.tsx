// File: RepositoryDataTable.tsx
"use client";

// Import necessary React hooks.
import  { useState, useEffect, forwardRef, useImperativeHandle, useMemo } from "react";
// Import useQuery from TanStack Query.
import { useQuery, useQueryClient } from '@tanstack/react-query';
// Import useRouter from TanStack Router.
import { useRouter } from '@tanstack/react-router';

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

// Define the ref interface so parent components can, for example, retrieve selected row names.
export interface RepositoryDataTableRef {
  getSelectedRowNames: () => string[];
}

// Main component implementation using forwardRef so methods can be exposed.
export const RepositoryDataTable = forwardRef<RepositoryDataTableRef, { tokenStatus: boolean; onSelectionChange?: (selectedRows: string[]) => void; }>(
  

  ({ tokenStatus, onSelectionChange }, ref) => {
    console.log('[RepositoryDataTable] Component rendering, tokenStatus:', tokenStatus);
    const queryClient = useQueryClient();
    
    // Get router instance to access URL info.
    const router = useRouter();
    console.log('[RepositoryDataTable] Current router state:', router.state.location);

    // Create a memoized object from the URL search parameters.
    // This converts the search string into an object so we can access 'page' and 'perPage'.
    const { pageIndex, perPage, filterValues } = OnboardingRoute.useSearch();
    
    

    // Manage an array of pagination cursors. The initial cursor is undefined.
    const [cursors, setCursors] = useState<(string | undefined)[]>([undefined]);
    console.log('[RepositoryDataTable] Current cursors array:', cursors);
    
    // Use TanStack Query to fetch repository data.
    const { data: repoData, isLoading, isFetching, status } = useQuery<PaginatedResponse<GitHubRepoSummary>>({
      queryKey: ['repositories', pageIndex, perPage,filterValues, cursors[pageIndex - 1]],
      // Fetch data using our provided API function; pass the current page, perPage, and cursor.
      queryFn: () => {
        console.log('[RepositoryDataTable] Fetching repositories with params:', {
          pageIndex,
          perPage,
          cursor: cursors[pageIndex - 1]
        });
        return fetchGitHubRepositories(pageIndex, perPage, filterValues, cursors[pageIndex - 1]);
      },
      enabled: tokenStatus, // Only perform the query if the token is valid.
      // Remove placeholderData to show loading state during pagination
      
    });

    console.log('[RepositoryDataTable] Query result:', { 
      isLoading, 
      isFetching,
      status,
      hasData: !!repoData, 
      itemCount: repoData?.items?.length || 0,
      hasNext: repoData?.has_next
    });

    // If the API returns a next_cursor and the cursors array is not long enough,
    // add the new cursor to the state (to support further pages).
    useEffect(() => {
      console.log('[RepositoryDataTable] Checking if we need to update cursors:', {
        nextCursor: repoData?.next_cursor,
        currentPage: pageIndex,
        cursorsLength: cursors.length
      });
      
      if (repoData?.next_cursor) {
        // Update the cursor for the next page, creating a new array with the updated cursor
        console.log('[RepositoryDataTable] Updating cursor for page', pageIndex);
        setCursors(prev => {
          const newCursors = [...prev];
          // If we're on page N, we want to set the cursor for page N+1
          if (pageIndex >= newCursors.length) {
            // Add the new cursor if we're at the end of the array
            newCursors.push(repoData.next_cursor);
          } else {
            // Update the existing cursor for the next page
            newCursors[pageIndex] = repoData.next_cursor;
          }
          return newCursors;
        });
      }
    }, [repoData, pageIndex]);

    // Get the column definitions (i.e., which columns to display) from an imported function.
    const columns = useMemo(() => {
      const cols = getRepositoryDataTableColumns();
      console.log('[RepositoryDataTable] Got column definitions:', cols.length, 'columns');
      return cols;
    }, []);

    // Use our custom hook to create the table instance.
    // This hook takes data, columns, pageCount, and initial pagination state.
    const { table } = useDataTableWithRouter({
      data: repoData?.items || [], // Use an empty array if no data.
      columns,
      // If there's another page, use -1; otherwise, use the current page number.
      pageCount: repoData?.has_next ? -1 : pageIndex,
      // Set the initial table state with the current pagination information.
      initialState: {
        columnPinning: { left: ['select'] },
        pagination: {
          pageIndex: pageIndex - 1,
          pageSize: perPage,
        },
      },
      // Tell the table how to uniquely identify a row (here using the repository name).
      getRowId: (row: GitHubRepoSummary): string => row.name,
    });

    // Prefetch the next page when getting close to it
    useEffect(() => {
      // Only prefetch if we have data, there's more data available, and we have a next cursor
      if (repoData?.has_next && repoData?.next_cursor && tokenStatus) {
        const nextPageIndex = pageIndex + 1;
        
        console.log('[RepositoryDataTable] Prefetching next page:', {
          nextPageIndex,
          nextCursor: repoData.next_cursor
        });
        
        // Create a query key for the next page
        const nextPageQueryKey = ['repositories', nextPageIndex, perPage, filterValues, repoData.next_cursor];
        
        // Only prefetch if we don't already have fresh data
        queryClient.prefetchQuery({
          queryKey: nextPageQueryKey,
          queryFn: () => fetchGitHubRepositories(nextPageIndex, perPage, filterValues, repoData.next_cursor),
          staleTime: 60 * 1000, // 1 minute - data stays fresh for 1 minute
        });
      }
    }, [repoData, pageIndex, perPage, filterValues, queryClient, tokenStatus, cursors]);

    console.log('[RepositoryDataTable] Table instance created:', {
      rowCount: table.getRowModel().rows.length,
      pageSize: table.getState().pagination.pageSize,
      pageIndex: table.getState().pagination.pageIndex,
      selectedRows: Object.keys(table.getState().rowSelection || {}).length,
      canNextPage: table.getCanNextPage(),
      canPreviousPage: table.getCanPreviousPage()
    });

    // Log pagination actions
    useEffect(() => {
      // Track when pagination state changes in the table
      console.log('[RepositoryDataTable] Table pagination state changed:', {
        pageIndex: table.getState().pagination.pageIndex,
        pageSize: table.getState().pagination.pageSize,
        routerPage: pageIndex,
        routerPerPage: perPage
      });
    }, [table.getState().pagination, pageIndex, perPage]);

    // Expose a method via the ref so a parent can call getSelectedRowNames.
    useImperativeHandle(ref, () => ({
      getSelectedRowNames: () => {
        const selectedRows = table.getSelectedRowModel().rows;
        const names = selectedRows.map(row => row.original.name);
        console.log('[RepositoryDataTable] Getting selected row names:', names);
        // Return an array of repository names for the selected rows.
        return names;
      }
    }), [table]);

    // If the selection state changes, call the onSelectionChange callback if provided.
    useEffect(() => {
      if (onSelectionChange) {
        const selectedRows = table.getSelectedRowModel().rows;
        const names = selectedRows.map(row => row.original.name);
        console.log('[RepositoryDataTable] Selection changed, notifying parent:', names);
        onSelectionChange(names);
      }
    }, [table.getState().rowSelection, onSelectionChange, table]);

    console.log('[RepositoryDataTable] Rendering data table');
    // Render the Dice UI DataTable component, passing the table instance and no extra action bar.
    return (
      <DataTable 
        table={table} 
        actionBar={null}
        isLoading={isFetching}
      >

          <DataTableToolbar table={table}>
            
          </DataTableToolbar>
      </DataTable>
    );
  }
);

// Set a display name for easier debugging in React DevTools.
RepositoryDataTable.displayName = "RepositoryDataTable";