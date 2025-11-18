// File: RepositoryDataTable.tsx
"use client";

// Import necessary React hooks.
import {
  useState,
  useEffect,
  useMemo,
} from "react";
// Import useQuery from TanStack Query.
import {
  useQuery,
  useQueryClient,
  keepPreviousData,
} from "@tanstack/react-query";
// Import useRouter from TanStack Router.
// import { useRouter } from '@tanstack/react-router';

// Import the Dice UI DataTable component which is built on TanStack Table.
import { DataTable } from "../data-table";
// Import the custom hook that binds table state with router-based URL parameters.
import { useDataTableWithRouter } from "@/hooks/use-data-table-with-router";
// Import the column definitions for this repository table.
import { getRepositoryDataTableColumns } from "./repository-data-table-columns";

// Import the API function to fetch repository data along with type definitions.
import {
  fetchGitHubRepositories,
  submitRepositoryConfig,
  type PaginatedResponse,
} from "@/lib/api";
import type { GitHubRepoSummary } from "@/types";
import { ProviderKey } from "@/types/credential-enums";
import { Route as OnboardingRoute } from "../../routes/_app.onboarding";
import { DataTableToolbar } from "../data-table-toolbar";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

// Main component implementation (React 19 style - no forwardRef needed)
export function RepositoryDataTable({
  tokenStatus
}: {
  tokenStatus: boolean
}) {
  const queryClient = useQueryClient();
  const { pageIndex, perPage, filterValues } = OnboardingRoute.useSearch();

  // Manage an array of pagination cursors. The initial cursor is undefined.
  const [cursors, setCursors] = useState<(string | undefined)[]>([undefined]);

  // Mutation for repository ingestion with toast notifications
  const ingestMutation = useMutation({
    mutationFn: (repo: GitHubRepoSummary) =>
      submitRepositoryConfig({
        repository_name: repo.name,
        repository_git_url: repo.git_url,
        repository_owner_name: repo.owner_name,
        repository_metadata: null, // Backend auto-detects
        provider_key: ProviderKey.GITHUB_OPEN,
      }),
    onSuccess: (_, repo) => {
      toast.success(
        `Successfully submitted repository ${repo.name} to code confluence graph engine`,
      );
      queryClient.invalidateQueries({ queryKey: ["repository-config"] });
    },
    onError: (error: Error, repo) => {
      toast.error(`Failed to submit repository ${repo.name}: ${error.message}`);
    },
  });

  // Use TanStack Query to fetch repository data.
  const {
    data: repoData,
    isFetching,
    isPlaceholderData,
  } = useQuery<PaginatedResponse<GitHubRepoSummary>>({
    queryKey: [
      "repositories",
      pageIndex,
      perPage,
      filterValues,
      cursors[pageIndex - 1],
    ],
    queryFn: () =>
      fetchGitHubRepositories(
        pageIndex,
        perPage,
        ProviderKey.GITHUB_OPEN,
        filterValues,
        cursors[pageIndex - 1],
      ),
    enabled: tokenStatus,
    placeholderData: keepPreviousData,
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnMount: false,
  });

  useEffect(() => {
    if (repoData?.next_cursor) {
      setCursors((prev) => {
        const newCursors = [...prev];
        if (pageIndex >= newCursors.length) {
          newCursors.push(repoData.next_cursor);
        } else {
          newCursors[pageIndex] = repoData.next_cursor;
        }
        return newCursors;
      });
    }
  }, [repoData, pageIndex]);

  // Build columns with the ingest callback
  const columns = useMemo(() => {
    return getRepositoryDataTableColumns({
      onIngest: (repo) => ingestMutation.mutate(repo),
    });
  }, [ingestMutation]);

  // 3️⃣ Initialize DiceUI DataTable
  const { table } = useDataTableWithRouter({
    data: repoData?.items || [],
    columns,
    pageCount: repoData?.has_next ? -1 : pageIndex,
    initialState: {
      pagination: {
        pageIndex: pageIndex - 1,
        pageSize: perPage,
      },
    },
    getRowId: (row: GitHubRepoSummary): string => row.name,
  });

  // Prefetch two pages ahead
  useEffect(() => {
    if (!tokenStatus || !repoData?.has_next || !repoData.next_cursor) return;

    // Prefetch page+1
    const cursor1: string = repoData.next_cursor;
    const pageToPrefetch1: number = pageIndex + 1;
    queryClient.prefetchQuery({
      queryKey: [
        "repositories",
        pageToPrefetch1,
        perPage,
        filterValues,
        cursor1,
      ],
      queryFn: () =>
        fetchGitHubRepositories(
          pageToPrefetch1,
          perPage,
          filterValues,
          cursor1,
        ),
    });

    // Also fetch page+1 data to obtain its cursor, then prefetch page+2
    fetchGitHubRepositories(pageToPrefetch1, perPage, filterValues, cursor1)
      .then((nextPageData: PaginatedResponse<GitHubRepoSummary>) => {
        if (nextPageData.next_cursor) {
          const cursor2: string = nextPageData.next_cursor;
          const pageToPrefetch2: number = pageIndex + 2;
          queryClient.prefetchQuery({
            queryKey: [
              "repositories",
              pageToPrefetch2,
              perPage,
              filterValues,
              cursor2,
            ],
            queryFn: () =>
              fetchGitHubRepositories(
                pageToPrefetch2,
                perPage,
                filterValues,
                cursor2,
              ),
          });
        }
      })
      .catch(() => {
        // ignore prefetch errors
      });
  }, [repoData, pageIndex, perPage, filterValues, queryClient, tokenStatus]);

  // Render DataTable
  return (
    <div className="w-full">
      <DataTable
        table={table}
        actionBar={null}
        isLoading={isFetching && !isPlaceholderData}
      >
        <DataTableToolbar table={table} />
      </DataTable>
    </div>
  );
}
