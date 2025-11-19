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
import { RefreshRepositoryDialog } from "./RefreshRepositoryDialog";
import { DeleteRepositoryDialog } from "./DeleteRepositoryDialog";
import { toast } from "sonner";
import { useAgentGenerationUIStore } from "@/stores/useAgentGenerationUIStore";
import { GenerateAgentsDialog } from "@/components/custom/GenerateAgentsDialog";
import { useModelConfig } from "@/hooks/useModelConfig";

import type { IngestedRepository } from "../../types";
import {
  getIngestedRepositories,
  refreshRepository,
  deleteRepository,
  getModelConfig,
} from "@/lib/api";

interface RowAction {
  row: import("@tanstack/react-table").Row<IngestedRepository>;
  variant: "refresh" | "delete";
}

export function IngestedRepositoriesDataTable(): React.ReactElement {
  const [rowAction, setRowAction] = useState<RowAction | null>(null);
  const isGenerationDialogOpen = useAgentGenerationUIStore(
    (s) => s.isDialogOpen,
  );
  const selectedRepository = useAgentGenerationUIStore(
    (s) => s.selectedRepository,
  );
  const closeGenerationDialog = useAgentGenerationUIStore((s) => s.closeDialog);
  const openGenerationDialog = useAgentGenerationUIStore((s) => s.openDialog);

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

  // Refresh mutation
  const refreshMutation = useMutation({
    mutationFn: (repository: IngestedRepository) =>
      refreshRepository(repository),
    onSuccess: () => {
      toast.success("Repository has been successfully submitted for refresh");
      queryClient.invalidateQueries({ queryKey: ["ingestedRepositories"] });
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
      queryClient.invalidateQueries({ queryKey: ["ingestedRepositories"] });
    },
    onError: () => {
      toast.error("Unable to delete the repository. Please try again.");
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

        openGenerationDialog(repository);
      } catch {
        toast.error(
          "Unable to verify model provider configuration. Please try again.",
        );
      }
    },
    [modelConfigQuery.data, openGenerationDialog, queryClient],
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

  const handleRefreshConfirm = () => {
    if (rowAction?.row.original) {
      refreshMutation.mutate(rowAction.row.original);
    }
    setRowAction(null);
  };

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

      <RefreshRepositoryDialog
        open={rowAction?.variant === "refresh"}
        onOpenChange={handleDialogClose}
        onConfirm={handleRefreshConfirm}
        repository={rowAction?.row.original || null}
      />

      <DeleteRepositoryDialog
        open={rowAction?.variant === "delete"}
        onOpenChange={handleDialogClose}
        onConfirm={handleDeleteConfirm}
        repository={rowAction?.row.original || null}
      />

      <GenerateAgentsDialog
        repository={selectedRepository}
        open={isGenerationDialogOpen}
        onOpenChange={closeGenerationDialog}
      />
    </div>
  );
}
