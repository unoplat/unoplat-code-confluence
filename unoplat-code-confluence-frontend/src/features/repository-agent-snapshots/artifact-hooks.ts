import React from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import {
  getRepositoryAgentArtifact,
  getRepositoryAgentSnapshot,
  type RepositoryArtifactReadFailure,
} from "@/lib/api";

import type { RepositoryAgentSnapshotScope } from "./collection";
import type { ArtifactManifestEntry } from "./schema";
import {
  assembleMarkdownArtifacts,
  toRepositoryArtifactAvailability,
  type RepositoryArtifactAvailability,
  type RepositoryMarkdownArtifactFile,
} from "./transformers";

// Stored Git identity comes only from the server, so every refresh reads again.
const artifactMetadataStaleTime = 0;
// Each file read makes several provider calls, so limit reads in flight.
const markdownBundleReadBatchSize = 4;

export type RepositoryArtifactMetadataState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; isRetrying: boolean; retry: () => void }
  | { status: "ready"; availability: RepositoryArtifactAvailability };

export type RepositoryArtifactFileState =
  | { status: "idle" }
  | { status: "loading" }
  | {
      status: "error";
      failure: RepositoryArtifactReadFailure;
      isRetrying: boolean;
      retry: () => void;
    }
  | { status: "ready"; content: string };

interface UseRepositoryArtifactMetadataOptions {
  scope: RepositoryAgentSnapshotScope | null;
  isRunActive: boolean;
  runStatus: string;
  liveRefreshKey: string | null;
}

interface UseRepositoryArtifactFileOptions {
  scope: RepositoryAgentSnapshotScope;
  commitSha: string;
  path: string | null;
  enabled: boolean;
}

interface UseRepositoryMarkdownBundleDownloadOptions {
  scope: RepositoryAgentSnapshotScope;
  commitSha: string;
  repositoryName: string;
  manifest: ArtifactManifestEntry[];
  isActive: boolean;
  onReady: (markdown: string) => void;
  onFailure: (failure: RepositoryArtifactReadFailure) => void;
}

export interface RepositoryMarkdownBundleDownload {
  hasMarkdownFiles: boolean;
  isPreparing: boolean;
  start: () => void;
}

const defaultLiveRefreshKey = JSON.stringify([null, null]);

export function getRepositoryArtifactMetadataQueryKey({
  owner,
  repository,
  runId,
}: RepositoryAgentSnapshotScope): string[] {
  return ["repositoryAgentArtifactMetadata", owner, repository, runId];
}

/**
 * Reads server-derived availability for one exact run. Run status and live
 * identity signals are part of the key, so a change starts a fresh read with no
 * placeholder from the earlier key.
 */
export function useRepositoryArtifactMetadata({
  scope,
  isRunActive,
  runStatus,
  liveRefreshKey,
}: UseRepositoryArtifactMetadataOptions): RepositoryArtifactMetadataState {
  const isEnabled = scope !== null;
  const query = useQuery({
    queryKey: [
      ...(scope ? getRepositoryArtifactMetadataQueryKey(scope) : ["disabled"]),
      runStatus,
      liveRefreshKey ?? defaultLiveRefreshKey,
    ],
    queryFn: async ({ signal }) => {
      if (!scope) {
        return null;
      }
      const metadata = await getRepositoryAgentSnapshot(
        scope.owner,
        scope.repository,
        scope.runId,
        signal,
      );
      if (metadata && metadata.repository_workflow_run_id !== scope.runId) {
        throw new Error("Snapshot metadata belongs to a different run");
      }
      return metadata;
    },
    enabled: isEnabled,
    staleTime: artifactMetadataStaleTime,
    retry: 1,
  });

  // A disabled query can still return cached data, and a failed refetch keeps
  // its last data, so neither case may reach the viewer.
  if (!isEnabled) {
    return { status: "idle" };
  }
  if (query.isError) {
    return {
      status: "error",
      isRetrying: query.isFetching,
      retry: () => {
        void query.refetch();
      },
    };
  }
  if (query.data === undefined) {
    return { status: "loading" };
  }
  return {
    status: "ready",
    availability: toRepositoryArtifactAvailability(query.data, isRunActive),
  };
}

/**
 * Reads one manifest file. The cache is isolated by owner, repository, run, saved
 * SHA and path. The SHA is a cache key only: the server resolves the commit.
 */
export function useRepositoryArtifactFile({
  scope,
  commitSha,
  path,
  enabled,
}: UseRepositoryArtifactFileOptions): RepositoryArtifactFileState {
  const isEnabled = enabled && path !== null;
  const query = useQuery<string, RepositoryArtifactReadFailure>({
    queryKey: [
      "repositoryAgentArtifact",
      scope.owner,
      scope.repository,
      scope.runId,
      commitSha,
      path,
    ],
    queryFn: ({ signal }) => {
      if (path === null) {
        throw new Error("No artifact is selected");
      }
      return getRepositoryAgentArtifact(
        scope.owner,
        scope.repository,
        scope.runId,
        path,
        signal,
      );
    },
    enabled: isEnabled,
    retry: false,
  });

  if (!isEnabled) {
    return { status: "idle" };
  }
  if (query.isError) {
    return {
      status: "error",
      failure: query.error,
      isRetrying: query.isFetching,
      retry: () => {
        void query.refetch();
      },
    };
  }
  if (query.data === undefined) {
    return { status: "loading" };
  }
  return { status: "ready", content: query.data };
}

async function readMarkdownArtifacts(
  scope: RepositoryAgentSnapshotScope,
  paths: string[],
  signal: AbortSignal,
): Promise<RepositoryMarkdownArtifactFile[]> {
  const files: RepositoryMarkdownArtifactFile[] = [];

  for (
    let start = 0;
    start < paths.length;
    start += markdownBundleReadBatchSize
  ) {
    const batch = await Promise.all(
      paths
        .slice(start, start + markdownBundleReadBatchSize)
        .map(async (path) => ({
          path,
          content: await getRepositoryAgentArtifact(
            scope.owner,
            scope.repository,
            scope.runId,
            path,
            signal,
          ),
        })),
    );
    files.push(...batch);
  }

  return files;
}

/**
 * Builds the aggregate Markdown download from the verified single-file API. It
 * reads only this manifest's Markdown files and delivers a result only if every
 * read succeeds. Closing the viewer or changing scope aborts the reads and
 * discards the result.
 */
export function useRepositoryMarkdownBundleDownload({
  scope,
  commitSha,
  repositoryName,
  manifest,
  isActive,
  onReady,
  onFailure,
}: UseRepositoryMarkdownBundleDownloadOptions): RepositoryMarkdownBundleDownload {
  const { owner, repository, runId } = scope;
  const controllerRef = React.useRef<AbortController | null>(null);
  const markdownPaths = manifest
    .filter((entry) => entry.kind === "markdown")
    .map((entry) => entry.path);

  const mutation = useMutation<
    string,
    RepositoryArtifactReadFailure,
    AbortSignal
  >({
    mutationFn: async (signal) =>
      assembleMarkdownArtifacts(
        repositoryName,
        commitSha,
        await readMarkdownArtifacts(scope, markdownPaths, signal),
      ),
  });

  React.useEffect(() => {
    if (!isActive) {
      return undefined;
    }

    return () => {
      controllerRef.current?.abort();
      controllerRef.current = null;
    };
  }, [isActive, owner, repository, runId, commitSha]);

  const start = (): void => {
    if (
      !isActive ||
      markdownPaths.length === 0 ||
      controllerRef.current ||
      mutation.isPending
    ) {
      return;
    }

    const controller = new AbortController();
    controllerRef.current = controller;
    mutation.mutate(controller.signal, {
      onSuccess: (markdown) => {
        if (controllerRef.current === controller) {
          onReady(markdown);
        }
      },
      onError: (failure) => {
        if (controllerRef.current === controller) {
          onFailure(failure);
        }
      },
      onSettled: () => {
        // Stops sibling reads still in flight after the first failure.
        controller.abort();
        if (controllerRef.current === controller) {
          controllerRef.current = null;
        }
      },
    });
  };

  return {
    hasMarkdownFiles: markdownPaths.length > 0,
    isPreparing: mutation.isPending,
    start,
  };
}
