import { useEffect, useMemo } from 'react';
import { useLiveQuery } from '@tanstack/react-db';

import {
  destroyRepositoryAgentSnapshotCollection,
  getRepositoryAgentSnapshotCollection,
  type RepositoryAgentSnapshotCollection,
  type RepositoryAgentSnapshotScope,
} from './collection';
import { type ParsedRepositoryAgentSnapshot, useParsedSnapshot } from './transformers';
import type { RepositoryAgentSnapshotRow } from './schema';

export interface UseRepositoryAgentSnapshotResult {
  snapshotRow: RepositoryAgentSnapshotRow | undefined;
  parsedSnapshot: ParsedRepositoryAgentSnapshot | null;
  status: string;
  isLoading: boolean;
  isReady: boolean;
  isError: boolean;
  collection: RepositoryAgentSnapshotCollection | undefined;
}

export function useRepositoryAgentSnapshot(scope: RepositoryAgentSnapshotScope | null | undefined): UseRepositoryAgentSnapshotResult {
  const memoizedScope = useMemo(() => {
    if (!scope) {
      return null;
    }
    return { owner: scope.owner, repository: scope.repository };
  }, [scope?.owner, scope?.repository]);

  const collection = useMemo(() => {
    return memoizedScope ? getRepositoryAgentSnapshotCollection(memoizedScope) : undefined;
  }, [memoizedScope?.owner, memoizedScope?.repository]);

  useEffect(() => {
    if (!memoizedScope || !collection) {
      return;
    }

    let isUnmounted = false;

    collection
      .preload()
      .catch((error) => {
        if (!isUnmounted) {
          console.error('Failed to preload repository agent snapshot collection', error);
        }
      });

    return () => {
      isUnmounted = true;
      void destroyRepositoryAgentSnapshotCollection(memoizedScope);
    };
  }, [memoizedScope?.owner, memoizedScope?.repository, collection]);

  const liveQueryResult = useLiveQuery(
    (q) => {
      if (!collection) return undefined;
      return q.from({ snapshots: collection });
    },
    [collection]
  );

  const snapshotRow = liveQueryResult?.data?.[0] as RepositoryAgentSnapshotRow | undefined;
  const parsedSnapshot = useParsedSnapshot(snapshotRow);

  return {
    snapshotRow,
    parsedSnapshot,
    status: liveQueryResult?.status || 'idle',
    isLoading: liveQueryResult?.isLoading || false,
    isReady: liveQueryResult?.isReady || false,
    isError: liveQueryResult?.isError || false,
    collection,
  };
}
