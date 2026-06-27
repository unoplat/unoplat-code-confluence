"use client";

import { useCallback, useEffect, useMemo } from "react";
import {
  InfiniteData,
  keepPreviousData,
  useInfiniteQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { parseAsInteger, parseAsString, useQueryState } from "nuqs";
import { toast } from "sonner";

import { DataTable } from "@/components/data-table/data-table";
import { DataTableSkeleton } from "@/components/data-table/data-table-skeleton";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { useDataTable } from "@/hooks/use-data-table";
import type { ApiError } from "@/lib/api";
import { addRepository, fetchGitHubRepositories } from "@/lib/api";
import type { GitHubRepoSummary, PaginatedResponse } from "@/types";
import { ProviderKey } from "@/types/credential-enums";

import { getRepositoryDataTableColumns } from "./repository-data-table-columns";

interface RepositoryDataTableProps {
  providerKey: ProviderKey;
}

export function RepositoryDataTable({ providerKey }: RepositoryDataTableProps) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const addRepositoryMutation = useMutation({
    mutationFn: (repo: GitHubRepoSummary) =>
      addRepository({
        repository_git_url: repo.git_url,
        provider_key: providerKey,
      }),
    onSuccess: (result, repo) => {
      if (result.already_added) {
        toast.info(`${repo.owner_name}/${repo.name} is already added.`, {
          description: "Manage this repository in Repository Operations.",
          action: {
            label: "Go to Repository Operations",
            onClick: () => {
              void navigate({ to: "/repositoryOperations" });
            },
          },
          duration: 8000,
        });
      } else {
        toast.success(`Added repository ${repo.owner_name}/${repo.name}.`, {
          description: "You can generate or update Agents.md from Repository Operations.",
          action: {
            label: "Go to Repository Operations",
            onClick: () => {
              void navigate({ to: "/repositoryOperations" });
            },
          },
          duration: 8000,
        });
      }
      queryClient.invalidateQueries({ queryKey: ["ingestedRepositories"] });
    },
    onError: (error: ApiError, repo) => {
      toast.error(`Failed to add repository ${repo.name}: ${error.message}`);
    },
  });

  const handleAddRepository = useCallback(
    (repo: GitHubRepoSummary) => addRepositoryMutation.mutate(repo),
    [addRepositoryMutation],
  );

  const columns = useMemo(
    () =>
      getRepositoryDataTableColumns({
        onAddRepository: handleAddRepository,
      }),
    [handleAddRepository],
  );

  const [pageValue] = useQueryState("page", parseAsInteger.withDefault(1));
  const [perPageValue] = useQueryState(
    "perPage",
    parseAsInteger.withDefault(10),
  );
  const [nameFilterValue] = useQueryState(
    "name",
    parseAsString.withDefault(""),
  );

  const perPage = perPageValue ?? 10;
  const pageIndexFromUrl = Math.max(pageValue - 1, 0);
  const normalizedNameFilter = nameFilterValue.trim();
  const activeNameFilter =
    normalizedNameFilter.length > 0 ? normalizedNameFilter : undefined;

  const repositoriesQueryKey = useMemo(
    () => ["repositories", providerKey, perPage, activeNameFilter ?? ""],
    [perPage, activeNameFilter, providerKey],
  );

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isError,
    isFetchingNextPage,
    isPending,
  } = useInfiniteQuery<
    PaginatedResponse<GitHubRepoSummary>,
    Error,
    PaginatedResponse<GitHubRepoSummary>,
    typeof repositoriesQueryKey,
    string | undefined
  >({
    queryKey: repositoriesQueryKey,
    queryFn: ({ pageParam }) =>
      fetchGitHubRepositories({
        perPage,
        providerKey,
        filterValues: activeNameFilter ? { name: activeNameFilter } : undefined,
        cursor: pageParam,
      }),
    initialPageParam: undefined,
    getNextPageParam: (lastPage) =>
      lastPage.has_next ? (lastPage.next_cursor ?? undefined) : undefined,
    maxPages: 10,
    enabled: true,
    placeholderData: keepPreviousData,
    staleTime: 1000 * 60 * 5,
    refetchOnMount: false,
  });
  const infiniteData = data as
    | InfiniteData<PaginatedResponse<GitHubRepoSummary>, string | undefined>
    | undefined;
  const pages = infiniteData?.pages ?? [];
  const totalFetchedPages = pages.length;
  const effectivePageIndex = useMemo(() => {
    if (totalFetchedPages === 0) return 0;
    if (pageIndexFromUrl >= totalFetchedPages) return totalFetchedPages - 1;
    return pageIndexFromUrl;
  }, [totalFetchedPages, pageIndexFromUrl]);

  const currentPage = pages[effectivePageIndex];
  const tableData = currentPage?.items ?? [];

  const pageCount = useMemo(() => {
    if (!data) return -1;
    if (totalFetchedPages === 0) return 1;
    return hasNextPage ? totalFetchedPages + 1 : totalFetchedPages;
  }, [data, hasNextPage, totalFetchedPages]);

  const { table } = useDataTable<GitHubRepoSummary>({
    data: tableData,
    columns,
    pageCount,
    initialState: {
      pagination: {
        pageIndex: 0,
        pageSize: 10,
      },
    },
    getRowId: (row) => row.git_url,
    clearOnDefault: true,
  });

  useEffect(() => {
    if (!data) return;
    if (!hasNextPage || isFetchingNextPage) return;
    if (pageIndexFromUrl < totalFetchedPages) return;

    void fetchNextPage();
  }, [
    data,
    pageIndexFromUrl,
    totalFetchedPages,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  ]);

  const showSkeleton = isPending && !data;

  return (
    <div className="w-full space-y-3">
      {isError && error && (
        <div className="border-destructive/40 bg-destructive/5 text-destructive rounded-md border p-3 text-sm">
          {error.message}
        </div>
      )}

      <div className={showSkeleton ? "invisible" : undefined}>
        <DataTable table={table}>
          <DataTableToolbar table={table} />
        </DataTable>

        {showSkeleton && (
          <div className="bg-background rounded-d pointer-events-none absolute inset-0">
            <DataTableSkeleton
              columnCount={columns.length}
              rowCount={10}
              filterCount={1}
              withViewOptions
              withPagination
            />
          </div>
        )}
      </div>
    </div>
  );
}
