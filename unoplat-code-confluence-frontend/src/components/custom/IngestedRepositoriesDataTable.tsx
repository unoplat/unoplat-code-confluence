"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  ColumnFiltersState,
  SortingState,
} from '@tanstack/react-table';

import { DataTable } from '@/components/data-table';
import { DataTableToolbar } from '@/components/data-table-toolbar';
import { getIngestedRepositoriesColumns } from './ingested-repositories-data-table-columns';
import { RefreshRepositoryDialog } from './RefreshRepositoryDialog';
import { DeleteRepositoryDialog } from './DeleteRepositoryDialog';
import { toast } from 'sonner';

import type { IngestedRepository } from '../../types';
import { 
  getIngestedRepositories, 
  refreshRepository, 
  deleteRepository 
} from '@/lib/api';

interface RowAction {
  row: import('@tanstack/react-table').Row<IngestedRepository>;
  variant: 'refresh' | 'delete';
}

export function IngestedRepositoriesDataTable(): React.ReactElement {
  const [rowAction, setRowAction] = useState<RowAction | null>(null);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [isRefreshDialogOpen, setIsRefreshDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  
  const queryClient = useQueryClient();

  // Fetch ingested repositories
  const {
    data: repositoriesData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['ingestedRepositories'],
    queryFn: getIngestedRepositories,
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 5, // Refetch every 5 seconds
    placeholderData: keepPreviousData,
    refetchOnMount: 'always',
    initialData: { repositories: [] },
    // Prevent re-renders during background fetches
    notifyOnChangeProps: ['data', 'error'],
    refetchIntervalInBackground: true,
  });

  const repositories = repositoriesData?.repositories ?? [];

  // Refresh mutation
  const refreshMutation = useMutation({
    mutationFn: (repository: IngestedRepository) => 
      refreshRepository(repository),
    onSuccess: () => {
      toast.success("Repository has been successfully submitted for refresh");
      queryClient.invalidateQueries({ queryKey: ['ingestedRepositories'] });
    },
    onError: () => {
      toast.error("Unable to refresh the repository. Please try again.");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (repository: IngestedRepository) => 
      deleteRepository(repository),
    onSuccess: () => {
      toast.success("The repository has been deleted successfully.");
      queryClient.invalidateQueries({ queryKey: ['ingestedRepositories'] });
    },
    onError: () => {
      toast.error("Unable to delete the repository. Please try again.");
    },
  });

  // Build columns with row action setter
  const columns = useMemo(() => {
    return getIngestedRepositoriesColumns({ setRowAction });
  }, []);

  // Initialize TanStack Table
  const table = useReactTable({
    data: repositories,
    columns,
    state: {
      columnFilters,
      sorting,
    },
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: setColumnFilters,
    onSortingChange: setSorting,
    initialState: {
      pagination: {
        pageSize: 7,
      },
    },
    getRowId: (row: IngestedRepository) => `${row.repository_owner_name}/${row.repository_name}`,
  });

  // Handle row actions
  useEffect(() => {
    if (rowAction) {
      if (rowAction.variant === 'refresh') {
        setIsRefreshDialogOpen(true);
      } else if (rowAction.variant === 'delete') {
        setIsDeleteDialogOpen(true);
      }
    }
  }, [rowAction]);

  const handleRefreshConfirm = () => {
    if (rowAction?.row.original) {
      refreshMutation.mutate(rowAction.row.original);
    }
    setIsRefreshDialogOpen(false);
    setRowAction(null);
  };

  const handleDeleteConfirm = () => {
    if (rowAction?.row.original) {
      deleteMutation.mutate(rowAction.row.original);
    }
    setIsDeleteDialogOpen(false);
    setRowAction(null);
  };

  const handleDialogClose = () => {
    setIsRefreshDialogOpen(false);
    setIsDeleteDialogOpen(false);
    setRowAction(null);
  };

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-sm text-destructive">
          Failed to load repositories. Please try again.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4">
      <DataTable
        table={table}
        isLoading={isLoading}
        actionBar={null}
      >
        <DataTableToolbar table={table} />
      </DataTable>

      <RefreshRepositoryDialog
        open={isRefreshDialogOpen}
        onOpenChange={handleDialogClose}
        onConfirm={handleRefreshConfirm}
        repository={rowAction?.row.original || null}
      />

      <DeleteRepositoryDialog
        open={isDeleteDialogOpen}
        onOpenChange={handleDialogClose}
        onConfirm={handleDeleteConfirm}
        repository={rowAction?.row.original || null}
      />
    </div>
  );
}