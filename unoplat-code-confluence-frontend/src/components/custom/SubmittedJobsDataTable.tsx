// File: SubmittedJobsDataTable.tsx
"use client";

// Import necessary React hooks.
import { useState, useEffect, useCallback } from "react";
// Import useQuery from TanStack Query.
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import React from "react";
import type { Row } from "@tanstack/react-table";

// Import the Dice UI DataTable component which is built on TanStack Table.
import { DataTable } from "@/components/data-table/data-table";
import { DataTableSkeleton } from "@/components/data-table/data-table-skeleton";
// Import TanStack Table core functions
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  ColumnFiltersState,
} from "@tanstack/react-table";
// Import the column definitions for this repository table.
import { submittedJobsColumns } from "./submitted-jobs-data-table-columns";

// Import the API function to fetch repository data along with type definitions.
import type { ParentWorkflowJobResponse } from "@/types";
import { getParentWorkflowJobs } from "@/lib/api";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
// Import dialog components for different operation types
import { JobStatusDialog } from "@/components/custom/JobStatusDialog";
import { GenerateAgentsDialog } from "@/components/custom/GenerateAgentsDialog";

interface RowAction {
  row: Row<ParentWorkflowJobResponse>;
  variant: string;
}

// Function to fetch parent workflow jobs from the API
const fetchParentWorkflowJobs = async (): Promise<
  ParentWorkflowJobResponse[]
> => {
  console.log(`[fetchParentWorkflowJobs] Fetching parent workflow jobs`);

  try {
    const response = await getParentWorkflowJobs();
    return response.jobs;
  } catch (error) {
    console.error("Error fetching parent workflow jobs:", error);
    return [];
  }
};

// Main component implementation
export function SubmittedJobsDataTable(): React.ReactElement {
  // 1️⃣ Track the current row action in state
  const [rowAction, setRowAction] = useState<RowAction | null>(null);

  // 2️⃣ Track filter state
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  // 3️⃣ Fetch parent workflow jobs data
  const { data: jobs, isInitialLoading } = useQuery({
    queryKey: ["parentWorkflowJobs"],
    queryFn: fetchParentWorkflowJobs,
    staleTime: 1000 * 60 * 1, // 1 minute
    refetchInterval: 1000 * 5, // Refetch every 5 seconds for active jobs
    refetchOnMount: "always",
    placeholderData: keepPreviousData,
    initialData: [],
    // Prevent re-renders during background fetches
    notifyOnChangeProps: ["data", "error"],
    refetchIntervalInBackground: true,
  });

  // 4️⃣ Create stable handleRowAction callback
  const handleRowAction = useCallback((action: RowAction) => {
    setRowAction(action);
  }, []);

  // 5️⃣ Initialize TanStack Table with client-side pagination
  const table = useReactTable({
    data: jobs,
    columns: submittedJobsColumns,
    meta: {
      handleRowAction,
    },
    state: {
      columnFilters,
    },
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(), // Enable client-side pagination
    getFilteredRowModel: getFilteredRowModel(), // Enable client-side filtering
    getSortedRowModel: getSortedRowModel(), // Enable client-side sorting
    onColumnFiltersChange: setColumnFilters,
    initialState: {
      pagination: {
        pageSize: 7, // Default page size
      },
    },
    getRowId: (row: ParentWorkflowJobResponse): string =>
      row.repository_workflow_run_id,
  });

  // State to control dialog visibility based on operation type
  const [isIngestionDialogOpen, setIsIngestionDialogOpen] = useState(false);
  const [isAgentDialogOpen, setIsAgentDialogOpen] = useState(false);

  // Handle row actions - open correct dialog based on operation type
  useEffect(() => {
    if (rowAction) {
      console.log(
        `[SubmittedJobsDataTable] Row action: ${rowAction.variant} on job ${rowAction.row.original.repository_workflow_run_id}`,
      );

      if (rowAction.variant === "view") {
        const operation = rowAction.row.original.operation;
        if (operation === "INGESTION") {
          setIsIngestionDialogOpen(true);
        } else if (
          operation === "AGENTS_GENERATION" ||
          operation === "AGENT_MD_UPDATE"
        ) {
          setIsAgentDialogOpen(true);
        }
      }
    }
  }, [rowAction]);

  // Handle ingestion dialog close
  const handleIngestionDialogOpenChange = (open: boolean) => {
    setIsIngestionDialogOpen(open);
    if (!open) {
      setRowAction(null);
    }
  };

  // Handle agent dialog close
  const handleAgentDialogOpenChange = (open: boolean) => {
    setIsAgentDialogOpen(open);
    if (!open) {
      setRowAction(null);
    }
  };

  // 6️⃣ Render DataTable with toolbar
  return (
    <div className="mx-auto w-full max-w-7xl px-4">
      {isInitialLoading ? (
        <DataTableSkeleton columnCount={7} rowCount={7} />
      ) : (
        <DataTable table={table} actionBar={null}>
          <DataTableToolbar table={table} />
        </DataTable>
      )}

      {/* Dialog for INGESTION operations */}
      <JobStatusDialog
        open={isIngestionDialogOpen}
        onOpenChange={handleIngestionDialogOpenChange}
        job={rowAction?.row.original || null}
      />

      {/* Dialog for AGENTS_GENERATION and AGENT_MD_UPDATE operations */}
      <GenerateAgentsDialog
        open={isAgentDialogOpen}
        onOpenChange={handleAgentDialogOpenChange}
        job={rowAction?.row.original ?? null}
      />
    </div>
  );
}
