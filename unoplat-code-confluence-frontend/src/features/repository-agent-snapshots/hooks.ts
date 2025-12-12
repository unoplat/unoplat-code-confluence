import { useLiveQuery } from "@tanstack/react-db";

import {
  getRepositoryAgentSnapshotCollection,
  type RepositoryAgentSnapshotScope,
  type RepositoryAgentSnapshotCollection,
} from "./collection";
import {
  type ParsedRepositoryAgentSnapshot,
  useParsedSnapshot,
} from "./transformers";
import type { RepositoryAgentSnapshotRow } from "./schema";

export interface UseRepositoryAgentSnapshotResult {
  snapshotRow: RepositoryAgentSnapshotRow | undefined;
  parsedSnapshot: ParsedRepositoryAgentSnapshot | null;
  status: string;
  isLoading: boolean;
  isReady: boolean;
  isError: boolean;
  collection: RepositoryAgentSnapshotCollection | undefined;
}

/**
 * Hook to query repository agent snapshot by composite primary key (owner + repository + runId).
 *
 * Uses TanStack DB's useLiveQuery for automatic reactivity - no external memoization needed.
 * Collection instances are cached in a singleton Map (see collection.ts), so retrieval is stable.
 *
 * @param scope - Composite key (owner + repository + runId). Pass null/undefined to skip querying.
 */
export function useRepositoryAgentSnapshot(
  scope: RepositoryAgentSnapshotScope | null | undefined,
): UseRepositoryAgentSnapshotResult {
  // Get or create collection from singleton cache
  // No memoization needed - getRepositoryAgentSnapshotCollection handles caching internally
  const collection = scope
    ? getRepositoryAgentSnapshotCollection(scope)
    : undefined;

  // Lifecycle is handled by the collection itself (startSync/gcTime).
  // Sync starts when the first live query subscribes and GC runs after gcTime.

  // useLiveQuery handles all reactivity internally via D2S (differential dataflow)
  // Collection reference is stable from singleton cache
  const liveQueryResult = useLiveQuery(
    (q) => {
      if (!collection) return undefined;
      return q.from({ snapshots: collection });
    },
    [collection],
  );

  const snapshotRow = liveQueryResult?.data?.[0] as
    | RepositoryAgentSnapshotRow
    | undefined;
  const parsedSnapshot = useParsedSnapshot(snapshotRow);

  return {
    snapshotRow,
    parsedSnapshot,
    status: liveQueryResult?.status || "idle",
    isLoading: liveQueryResult?.isLoading || false,
    isReady: liveQueryResult?.isReady || false,
    isError: liveQueryResult?.isError || false,
    collection,
  };
}
