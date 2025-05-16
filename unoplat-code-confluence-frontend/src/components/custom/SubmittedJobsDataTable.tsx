// File: SubmittedJobsDataTable.tsx
"use client";

// Import necessary React hooks.
import { useState, useEffect, useMemo } from "react";
// Import useQuery from TanStack Query.
import { useQuery } from '@tanstack/react-query';
import React from "react";

// Import the Dice UI DataTable component which is built on TanStack Table.
import { DataTable } from '../data-table';
// Import TanStack Table core functions
import { 
  useReactTable, 
  getCoreRowModel, 
  getPaginationRowModel,
  getFilteredRowModel, 
  getSortedRowModel,
  ColumnFiltersState
} from "@tanstack/react-table";
// Import the column definitions for this repository table.
import { getSubmittedJobsDataTableColumns } from "./submitted-jobs-data-table-columns";

// Import the API function to fetch repository data along with type definitions.
import type { ParentWorkflowJobResponse } from "../../types";
import { getParentWorkflowJobs } from "../../lib/api";
import { DataTableToolbar } from "../data-table-toolbar";
// Import the new JobStatusDialog component
import { JobStatusDialog } from "./JobStatusDialog";



interface RowAction<T> {
  row: import('@tanstack/react-table').Row<T>;
  variant: string;
}

// Function to fetch parent workflow jobs from the API
const fetchParentWorkflowJobs = async (): Promise<ParentWorkflowJobResponse[]> => {
  console.log(`[fetchParentWorkflowJobs] Fetching parent workflow jobs`);
  
  try {
    const response = await getParentWorkflowJobs();
    return response.jobs;
  } catch (error) {
    console.error('Error fetching parent workflow jobs:', error);
    return [];
  }
};

// Main component implementation
export function SubmittedJobsDataTable(): React.ReactElement {
  // 1️⃣ Track the current row action in state
  const [rowAction, setRowAction] = useState<RowAction<ParentWorkflowJobResponse> | null>(null);
  
  // 2️⃣ Track filter state
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  
  // 3️⃣ Fetch parent workflow jobs data
  const {
    data: jobs = [],
    isFetching,
  } = useQuery({
    queryKey: ['parentWorkflowJobs'],
    queryFn: fetchParentWorkflowJobs,
    staleTime: 1000 * 60 * 1, // 1 minute
    refetchInterval: 1000 * 30, // Refetch every 30 seconds for active jobs
  });
  
  
  // 4️⃣ Build columns with the row action setter
  const columns = useMemo(() => {
    return getSubmittedJobsDataTableColumns({ setRowAction });
  }, []);
  
  // 5️⃣ Initialize TanStack Table with client-side pagination
  const table = useReactTable({
    data: jobs,
    columns,
    state: {
      columnFilters,
    },
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(), // Enable client-side pagination
    getFilteredRowModel: getFilteredRowModel(),     // Enable client-side filtering
    getSortedRowModel: getSortedRowModel(),         // Enable client-side sorting
    onColumnFiltersChange: setColumnFilters,
    initialState: {
      pagination: {
        pageSize: 7, // Default page size
      },
    },
    getRowId: (row: ParentWorkflowJobResponse): string => row.repository_workflow_run_id,
  });
  
  // State to control the visibility of the JobStatusDialog
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Handle row actions
  useEffect(() => {
    if (rowAction) {
      console.log(`[SubmittedJobsDataTable] Row action: ${rowAction.variant} on job ${rowAction.row.original.repository_workflow_run_id}`);
      
      // Implement action handling here
      if (rowAction.variant === 'view') {
        setIsDialogOpen(true);
      }
    }
  }, [rowAction]);
  
  // Handle dialog close
  const handleDialogOpenChange = (open: boolean) => {
    setIsDialogOpen(open);
    if (!open) {
      // Clear row action when dialog is closed
      setRowAction(null);
    }
  };
  
  // 4️⃣ Render DataTable with toolbar
  return (
    <div className="w-full max-w-7xl mx-auto px-4">
      <DataTable
        table={table}
        actionBar={null}
        isLoading={isFetching}
      >
        <DataTableToolbar table={table} />
      </DataTable>
      
      {/* Use the new JobStatusDialog component */}
      <JobStatusDialog 
        open={isDialogOpen} 
        onOpenChange={handleDialogOpenChange} 
        job={rowAction?.row.original || null} 
      />
    </div>
  );
}
