"use client";

import React, { useState, useMemo, useCallback } from "react";
import {
  useQuery,
  useMutation,
  useQueryClient,
  keepPreviousData,
} from "@tanstack/react-query";

import { DataTable } from "@/components/data-table/data-table";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { DataTableSkeleton } from "@/components/data-table/data-table-skeleton";
import { useDataTable } from "@/hooks/use-data-table";
import { getIngestedRepositoriesColumns } from "./ingested-repositories-data-table-columns";
import { DeleteRepositoryDialog } from "./DeleteRepositoryDialog";
import { toast } from "sonner";
import { useModelConfig } from "@/hooks/useModelConfig";

import type { IngestedRepository } from "../../types";
import {
  getIngestedRepositories,
  updateAgentMd,
  deleteRepository,
  getModelConfig,
} from "@/lib/api";

interface RowAction {
  row: import("@tanstack/react-table").Row<IngestedRepository>;
  variant: "delete";
}

export function IngestedRepositoriesDataTable(): React.ReactElement {
  const [rowAction, setRowAction] = useState<RowAction | null>(null);

  const queryClient = useQueryClient();
  const modelConfigQuery = useModelConfig();

  // Fetch ingested repositories
  const {
    data: repositoriesData,
    isPending,
    error,
  } = useQuery({
    queryKey: ["ingestedRepositories"],
    queryFn: getIngestedRepositories,
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 5, // Refetch every 5 seconds
    placeholderData: keepPreviousData,
    refetchOnMount: "always",
    initialData: { repositories: [] },
    // Prevent re-renders during background fetches
    notifyOnChangeProps: ["data", "error"],
    refetchIntervalInBackground: true,
  });

  const repositories = repositoriesData?.repositories ?? [];

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (repository: IngestedRepository) =>
      deleteRepository(repository),
    onSuccess: () => {
      toast.success("The repository has been deleted successfully.");
      queryClient.invalidateQueries({ queryKey: ["ingestedRepositories"] });
    },
    onError: () => {
      toast.error("Unable to delete the repository. Please try again.");
    },
  });

  // Agent MD update mutation - starts unified refresh-then-generate flow
  const agentMdUpdateMutation = useMutation({
    mutationFn: (repository: IngestedRepository) => updateAgentMd(repository),
    onSuccess: (_data, repository) => {
      toast.success(
        `Generate/Update Agents.md submitted for ${repository.repository_owner_name}/${repository.repository_name}. View progress in Operations.`,
      );
      queryClient.invalidateQueries({ queryKey: ["ingestedRepositories"] });
      queryClient.invalidateQueries({ queryKey: ["parentWorkflowJobs"] });
    },
    onError: (error, repository) => {
      const errorMessage =
        error &&
        typeof error === "object" &&
        "message" in error &&
        typeof error.message === "string"
          ? error.message
          : `Failed to submit Generate/Update Agents.md for ${repository.repository_owner_name}/${repository.repository_name}. Please try again.`;

      toast.error(errorMessage);
    },
  });

  // Build columns with row action setter
  const handleGenerateAgents = useCallback(
    async (repository: IngestedRepository) => {
      try {
        let config = modelConfigQuery.data;

        if (typeof config === "undefined") {
          config = await queryClient.fetchQuery({
            queryKey: ["model-config"],
            queryFn: getModelConfig,
          });
        }

        if (!config) {
          toast.error("Please set model provider in model providers setting.");
          return;
        }

        agentMdUpdateMutation.mutate(repository);
      } catch {
        toast.error(
          "Unable to verify model provider configuration. Please try again.",
        );
      }
    },
    [modelConfigQuery.data, agentMdUpdateMutation, queryClient],
  );

  const columns = useMemo(() => {
    return getIngestedRepositoriesColumns({
      setRowAction,
      onGenerateAgents: handleGenerateAgents,
    });
  }, [handleGenerateAgents]);

  // Initialize TanStack Table with URL state management
  const { table } = useDataTable({
    data: repositories,
    columns,
    pageCount: -1, // Client-side pagination (backend doesn't support server pagination yet)
    initialState: {
      pagination: {
        pageIndex: 0,
        pageSize: 10,
      },
    },
    getRowId: (row: IngestedRepository) =>
      `${row.repository_owner_name}/${row.repository_name}`,
  });

  const handleDeleteConfirm = () => {
    if (rowAction?.row.original) {
      deleteMutation.mutate(rowAction.row.original);
    }
    setRowAction(null);
  };

  const handleDialogClose = () => {
    setRowAction(null);
  };

  if (error) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-destructive text-sm">
          Failed to load repositories. Please try again.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-7xl px-4">
      {isPending ? (
        <DataTableSkeleton
          columnCount={4}
          rowCount={10}
          filterCount={3}
          withViewOptions
          withPagination
        />
      ) : (
        <DataTable table={table}>
          <DataTableToolbar table={table} />
        </DataTable>
      )}

      <DeleteRepositoryDialog
        open={rowAction?.variant === "delete"}
        onOpenChange={handleDialogClose}
        onConfirm={handleDeleteConfirm}
        repository={rowAction?.row.original || null}
      />
    </div>
  );
}
