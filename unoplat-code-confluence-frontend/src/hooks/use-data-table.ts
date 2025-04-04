import { useReactTable } from '@tanstack/react-table';
import type { 
  ColumnDef, 
  ColumnFiltersState, 
  SortingState, 
  VisibilityState, 
  PaginationState, 
  RowSelectionState,
  OnChangeFn
} from '@tanstack/react-table';
import { useState } from 'react';
import { useRouter } from '@tanstack/react-router';

interface UseDataTableProps<TData> {
  data: TData[];
  columns: ColumnDef<TData, any>[];
  pageCount: number;
  initialState?: {
    sorting?: SortingState;
    pagination?: PaginationState;
    columnFilters?: ColumnFiltersState;
    columnVisibility?: VisibilityState;
    rowSelection?: RowSelectionState;
  };
  manualPagination?: boolean;
  manualFiltering?: boolean;
  manualSorting?: boolean;
  enableRowSelection?: boolean;
  onRowSelectionChange?: OnChangeFn<RowSelectionState>;
  onPaginationChange?: OnChangeFn<PaginationState>;
  onSortingChange?: OnChangeFn<SortingState>;
  onColumnFiltersChange?: OnChangeFn<ColumnFiltersState>;
  getCoreRowModel: any;
  getSortedRowModel?: any;
  getPaginationRowModel?: any;
  getFilteredRowModel?: any;
}

/**
 * Custom hook for managing data table state.
 * 
 * This hook provides a clean abstraction for TanStack Table that handles:
 * 1. State management for sorting, pagination, column filters, visibility and row selection
 * 2. Callback handling for state changes
 * 3. Proper initialization from initial state
 * 
 * Note: While this hook doesn't directly use TanStack Router for URL state,
 * the parent component can connect the onPaginationChange, onSortingChange, etc.
 * callbacks to router.navigate({ search: {...} }) to achieve URL-based persistence.
 * 
 * Example integration with TanStack Router in a parent component:
 * 
 * ```tsx
 * const router = useRouter();
 * 
 * const handlePaginationChange = (newPagination) => {
 *   router.navigate({
 *     search: {
 *       ...router.state.search,
 *       pagination: newPagination
 *     }
 *   });
 * };
 * ```
 */
export function useDataTable<TData>({
  data,
  columns,
  pageCount,
  initialState,
  manualPagination = false,
  manualFiltering = false,
  manualSorting = false,
  enableRowSelection = false,
  onRowSelectionChange,
  onPaginationChange,
  onSortingChange,
  onColumnFiltersChange,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
}: UseDataTableProps<TData>) {
  const router = useRouter();
  const currentSearch = (router.state as any).search || {};
  const urlSorting = (currentSearch.sorting as SortingState | undefined) || initialState?.sorting || [];
  const [sorting, setSorting] = useState<SortingState>(urlSorting);
  const urlPagination = (currentSearch.pagination as PaginationState | undefined) || initialState?.pagination || { pageIndex: 0, pageSize: 10 };
  const [pagination, setPagination] = useState<PaginationState>(urlPagination);
  const urlRowSelection = (currentSearch.rowSelection as RowSelectionState | undefined) || initialState?.rowSelection || {};
  const [rowSelection, setRowSelection] = useState<RowSelectionState>(urlRowSelection);
  
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>(
    initialState?.columnVisibility || {}
  );
  
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>(
    initialState?.columnFilters || []
  );

  // Event handlers that call back to parent components
  const handlePaginationChange: OnChangeFn<PaginationState> = (updaterOrValue): PaginationState => {
    const newValue = typeof updaterOrValue === 'function' ? updaterOrValue(pagination) : updaterOrValue;
    setPagination(newValue);
    if (onPaginationChange) {
      onPaginationChange(newValue);
    }
    return newValue;
  };

  const handleSortingChange: OnChangeFn<SortingState> = (updaterOrValue): SortingState => {
    const newValue = typeof updaterOrValue === 'function' ? updaterOrValue(sorting) : updaterOrValue;
    setSorting(newValue);
    if (onSortingChange) {
      onSortingChange(newValue);
    }
    return newValue;
  };

  const handleColumnFiltersChange: OnChangeFn<ColumnFiltersState> = (updaterOrValue) => {
    setColumnFilters((prev) => {
      const newValue = typeof updaterOrValue === 'function' ? updaterOrValue(prev) : updaterOrValue;
      if (onColumnFiltersChange) {
        onColumnFiltersChange(newValue);
      }
      return newValue;
    });
  };

  const handleRowSelectionChange: OnChangeFn<RowSelectionState> = (updaterOrValue): RowSelectionState => {
    const newValue = typeof updaterOrValue === 'function' ? updaterOrValue(rowSelection) : updaterOrValue;
    setRowSelection(newValue);
    if (onRowSelectionChange) {
      onRowSelectionChange(newValue);
    }
    return newValue;
  };

  // Create table instance
  const table = useReactTable({
    data,
    columns,
    pageCount,
    state: {
      sorting,
      pagination,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
    manualPagination,
    manualFiltering,
    manualSorting,
    enableRowSelection,
    onRowSelectionChange: handleRowSelectionChange,
    onPaginationChange: handlePaginationChange,
    onSortingChange: handleSortingChange,
    onColumnFiltersChange: handleColumnFiltersChange,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel ? getSortedRowModel() : undefined,
    getPaginationRowModel: getPaginationRowModel ? getPaginationRowModel() : undefined,
    getFilteredRowModel: getFilteredRowModel ? getFilteredRowModel() : undefined,
  });

  return {
    table,
  };
} 