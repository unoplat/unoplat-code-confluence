// File: use-data-table-with-router.ts
"use client";

// Import React (for hooks) and the core functions from TanStack Table.
import {
  useReactTable,
  type TableOptions,
  type TableState,
  getCoreRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFacetedMinMaxValues,
  type PaginationState,
} from '@tanstack/react-table';
// Import useRouter and useSearch from TanStack Router.
import { useRouter } from '@tanstack/react-router';
// Import type from TanStack Table.
import type { Table, Updater } from '@tanstack/react-table';
import React from 'react';
import { Route as OnboardingRoute } from '../routes/_app.onboarding';


// Define the props that the hook accepts.
export interface UseDataTableWithRouterProps<TData> extends Omit<TableOptions<TData>, 'state' | 'getCoreRowModel' | 'manualFiltering' | 'manualPagination' | 'manualSorting'> {
  initialState?: Partial<TableState>;
  pageCount?: number; // Add pageCount prop
}

// Helper function to handle pagination changes that updates URL search params

// The custom hook that links table state with URL-managed pagination.
export function useDataTableWithRouter<TData>(props: UseDataTableWithRouterProps<TData>): { table: Table<TData> } {
  console.log('[useDataTableWithRouter] Hook called with props:', {
    columns: props.columns.length,
    dataLength: props.data.length,
    initialState: props.initialState,
    pageCount: props.pageCount
  });

  // Extract properties for table configuration.
  const { data, columns, initialState, pageCount, ...tableProps } = props;
  // Get the current router instance.
  const router = useRouter();

  const { pageIndex, perPage } = OnboardingRoute.useSearch();

  const customPaginationState: PaginationState = React.useMemo(() => {
    return {
      pageIndex: pageIndex - 1, // zero-based index
      pageSize: perPage,
    };
  }, [pageIndex, perPage]);
  
  const onPaginationChange = React.useCallback(
    (updaterOrValue: Updater<PaginationState>) => {
      console.log('[useDataTable] onPaginationChange called with:', updaterOrValue);
      let newPagination: PaginationState;
      if (typeof updaterOrValue === "function") {
        newPagination = updaterOrValue(customPaginationState);
        console.log('[useDataTable] New pagination (functional):', newPagination);
      } else {
        newPagination = updaterOrValue;
        console.log('[useDataTable] New pagination (value):', newPagination);
      }
      
      router.navigate({
        to: OnboardingRoute.fullPath,
        search: {
          pageIndex: (newPagination.pageIndex+1),
          perPage: newPagination.pageSize,
        },
      });
    },
    [customPaginationState,pageIndex,perPage],
  );

  
  const table = useReactTable({
    ...tableProps,
    data,
    columns,
    // Merge the initial state with our computed pagination.
    state: {
      ...initialState,
      pagination: customPaginationState,
    },
    onPaginationChange,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    manualPagination: true,
    manualFiltering: true,
    pageCount: pageCount !== undefined ? pageCount : -1, // Use provided pageCount or default to -1 (unknown)
  });

  console.log('[useDataTableWithRouter] Table instance created:', {
    rowCount: table.getRowModel().rows.length,
    columnCount: table.getAllColumns().length,
    pageCount: table.getPageCount(),
    currentPage: table.getState().pagination.pageIndex,
    canNextPage: table.getCanNextPage(),
    canPreviousPage: table.getCanPreviousPage()
  });

  // Return the table instance to be used by the component.
  return { table };
}