import { useLiveInfiniteQuery, useLiveQuery } from "@tanstack/react-db";

import {
  getRepositoryAgentCodebaseProgressCollection,
  getRepositoryAgentEventCollection,
  getRepositoryAgentSnapshotCollection,
  type RepositoryAgentCodebaseProgressCollection,
  type RepositoryAgentEventCollection,
  type RepositoryAgentSnapshotCollection,
  type RepositoryAgentSnapshotScope,
} from "./collection";
import {
  parseCodebaseProgressRows,
  parseSnapshotRow,
  type ParsedRepositoryAgentSnapshot,
  type RepositoryAgentCodebaseState,
} from "./transformers";
import type {
  RepositoryAgentCodebaseProgressRow,
  RepositoryAgentEvent,
  RepositoryAgentSnapshotRow,
} from "./schema";

const defaultHistoryPageSize = 50;

export interface UseRepositoryAgentSnapshotResult {
  snapshotRow: RepositoryAgentSnapshotRow | undefined;
  parsedSnapshot: ParsedRepositoryAgentSnapshot | null;
  status: string;
  isLoading: boolean;
  isReady: boolean;
  isError: boolean;
  collection: RepositoryAgentSnapshotCollection | undefined;
}

export interface UseRepositoryAgentCodebaseProgressResult {
  progressRows: RepositoryAgentCodebaseProgressRow[];
  codebases: RepositoryAgentCodebaseState[];
  status: string;
  isLoading: boolean;
  isReady: boolean;
  isError: boolean;
  collection: RepositoryAgentCodebaseProgressCollection | undefined;
}

export interface UseRepositoryAgentEventHistoryResult {
  events: RepositoryAgentEvent[];
  status: string;
  isLoading: boolean;
  isReady: boolean;
  isError: boolean;
  hasOlderHistory: boolean;
  isFetchingOlderHistory: boolean;
  loadOlderHistory: () => void;
  collection: RepositoryAgentEventCollection;
}

export function useRepositoryAgentSnapshot(
  scope: RepositoryAgentSnapshotScope | null | undefined,
): UseRepositoryAgentSnapshotResult {
  const collection = scope
    ? getRepositoryAgentSnapshotCollection(scope)
    : undefined;
  const liveQueryResult = useLiveQuery(
    (q) => {
      if (!collection) {
        return undefined;
      }

      return q.from({ snapshots: collection });
    },
    [collection],
  );

  const snapshotRow = liveQueryResult?.data?.[0] as
    | RepositoryAgentSnapshotRow
    | undefined;

  return {
    snapshotRow,
    parsedSnapshot: snapshotRow ? parseSnapshotRow(snapshotRow) : null,
    status: liveQueryResult?.status || "idle",
    isLoading: liveQueryResult?.isLoading || false,
    isReady: liveQueryResult?.isReady || false,
    isError: liveQueryResult?.isError || false,
    collection,
  };
}

export function useRepositoryAgentCodebaseProgress(
  scope: RepositoryAgentSnapshotScope | null | undefined,
): UseRepositoryAgentCodebaseProgressResult {
  const collection = scope
    ? getRepositoryAgentCodebaseProgressCollection(scope)
    : undefined;
  const liveQueryResult = useLiveQuery(
    (q) => {
      if (!collection) {
        return undefined;
      }

      return q
        .from({ progress: collection })
        .orderBy(({ progress }) => progress.codebase_name, "asc");
    },
    [collection],
  );

  const progressRows = (liveQueryResult?.data ?? []) as Array<RepositoryAgentCodebaseProgressRow>;

  return {
    progressRows,
    codebases: parseCodebaseProgressRows(progressRows),
    status: liveQueryResult?.status || "idle",
    isLoading: liveQueryResult?.isLoading || false,
    isReady: liveQueryResult?.isReady || false,
    isError: liveQueryResult?.isError || false,
    collection,
  };
}

export function useRepositoryAgentEventHistory(
  scope: RepositoryAgentSnapshotScope,
  codebaseName: string,
  pageSize: number = defaultHistoryPageSize,
): UseRepositoryAgentEventHistoryResult {
  const normalizedCodebaseName =
    codebaseName.trim().length > 0 ? codebaseName : "__empty__";
  const collection = getRepositoryAgentEventCollection({
    ...scope,
    codebaseName: normalizedCodebaseName,
  });
  const liveQueryResult = useLiveInfiniteQuery(
    (q) =>
      q
        .from({ events: collection })
        .orderBy(({ events }) => events.event_id, "desc"),
    {
      pageSize,
    },
    [scope.owner, scope.repository, scope.runId, normalizedCodebaseName, pageSize],
  );
  const eventsDescending = (liveQueryResult.data ?? []) as Array<RepositoryAgentEvent>;

  return {
    events: [...eventsDescending].reverse(),
    status: liveQueryResult.status,
    isLoading: liveQueryResult.isLoading,
    isReady: liveQueryResult.isReady,
    isError: liveQueryResult.isError,
    hasOlderHistory: liveQueryResult.hasNextPage,
    isFetchingOlderHistory: liveQueryResult.isFetchingNextPage,
    loadOlderHistory: liveQueryResult.fetchNextPage,
    collection,
  };
}
