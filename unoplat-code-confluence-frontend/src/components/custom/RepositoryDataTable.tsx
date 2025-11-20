"use client";

import { useCallback, useEffect, useMemo } from "react";
import {
  InfiniteData,
  keepPreviousData,
  useInfiniteQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { parseAsInteger, parseAsString, useQueryState } from "nuqs";
import { toast } from "sonner";

import { DataTable } from "@/components/data-table/data-table";
import { DataTableSkeleton } from "@/components/data-table/data-table-skeleton";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { useDataTable } from "@/hooks/use-data-table";
import { fetchGitHubRepositories, submitRepositoryConfig } from "@/lib/api";
import type { GitHubRepoSummary, PaginatedResponse } from "@/types";
import { ProviderKey } from "@/types/credential-enums";

import { getRepositoryDataTableColumns } from "./repository-data-table-columns";

interface RepositoryDataTableProps {
  tokenStatus: boolean;
}

export function RepositoryDataTable({ tokenStatus }: RepositoryDataTableProps) {
  const queryClient = useQueryClient();

  const ingestMutation = useMutation({
    mutationFn: (repo: GitHubRepoSummary) =>
      submitRepositoryConfig({
        repository_name: repo.name,
        repository_git_url: repo.git_url,
        repository_owner_name: repo.owner_name,
        repository_metadata: null,
        provider_key: ProviderKey.GITHUB_OPEN,
      }),
    onSuccess: (_, repo) => {
      toast.success(
        `Successfully submitted repository ${repo.name} to code confluence graph engine`,
      );
      queryClient.invalidateQueries({ queryKey: ["repository-config"] });
    },
    onError: (error, repo) => {
      toast.error(`Failed to submit repository ${repo.name}: ${error.message}`);
    },
  });

  const handleIngest = useCallback(
    (repo: GitHubRepoSummary) => ingestMutation.mutate(repo),
    [ingestMutation],
  );

  const columns = useMemo(
    () =>
      getRepositoryDataTableColumns({
        onIngest: handleIngest,
      }),
    [handleIngest],
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
    () => [
      "repositories",
      ProviderKey.GITHUB_OPEN,
      perPage,
      activeNameFilter ?? "",
    ],
    [perPage, activeNameFilter],
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
        providerKey: ProviderKey.GITHUB_OPEN,
        filterValues: activeNameFilter ? { name: activeNameFilter } : undefined,
        cursor: pageParam,
      }),
    initialPageParam: undefined,
    getNextPageParam: (lastPage) =>
      lastPage.has_next ? (lastPage.next_cursor ?? undefined) : undefined,
    maxPages: 10,
    enabled: tokenStatus,
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
    if (!tokenStatus || !data) return -1;
    if (totalFetchedPages === 0) return 1;
    return hasNextPage ? totalFetchedPages + 1 : totalFetchedPages;
  }, [tokenStatus, data, hasNextPage, totalFetchedPages]);

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
    getRowId: (row) => row.name,
    clearOnDefault: true,
  });

  useEffect(() => {
    if (!tokenStatus || !data) return;
    if (!hasNextPage || isFetchingNextPage) return;
    if (pageIndexFromUrl < totalFetchedPages) return;

    void fetchNextPage();
  }, [
    tokenStatus,
    data,
    pageIndexFromUrl,
    totalFetchedPages,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  ]);

  if (!tokenStatus) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-muted-foreground text-sm">
          Connect your GitHub account to browse repositories.
        </p>
      </div>
    );
  }

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
          <div className="bg-background pointer-events-none absolute inset-0 rounded-md">
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
