import { createCollection } from "@tanstack/react-db";
import { electricCollectionOptions } from "@tanstack/electric-db-collection";

import { env } from "@/lib/env";

import {
  repositoryAgentCodebaseProgressRowSchema,
  repositoryAgentEventSchema,
  repositoryAgentSnapshotRowSchema,
  type RepositoryAgentCodebaseProgressRow,
  type RepositoryAgentEvent,
  type RepositoryAgentSnapshotRow,
} from "./schema";

// Scope for querying by composite primary key (owner + repository + runId)
export interface RepositoryAgentSnapshotScope {
  owner: string;
  repository: string;
  runId: string;
}

export interface RepositoryAgentCodebaseScope
  extends RepositoryAgentSnapshotScope {
  codebaseName: string;
}

const electricShapeUrl = `${env.electricBaseUrl.replace(/\/$/, "")}/v1/shape`;
const collectionGcTime = 1000 * 60 * 2;
const electricNumericParser = {
  numeric: (value: string): number => Number(value),
};

// Create scope key for composite PK queries
const createScopeKey = ({
  owner,
  repository,
  runId,
}: RepositoryAgentSnapshotScope): string => `${owner}/${repository}/${runId}`;

const createCodebaseScopeKey = ({
  owner,
  repository,
  runId,
  codebaseName,
}: RepositoryAgentCodebaseScope): string =>
  `${owner}/${repository}/${runId}/${codebaseName}`;

function createSnapshotCollection({
  owner,
  repository,
  runId,
}: RepositoryAgentSnapshotScope) {
  return createCollection(
    electricCollectionOptions({
      id: `repository-agent-snapshots-${owner}-${repository}-${runId}`,
      schema: repositoryAgentSnapshotRowSchema,
      getKey: (row: RepositoryAgentSnapshotRow) =>
        `${row.repository_owner_name}/${row.repository_name}/${row.repository_workflow_run_id}`,
      startSync: false,
      gcTime: collectionGcTime,
      syncMode: "eager",
      shapeOptions: {
        url: electricShapeUrl,
        params: {
          table: "repository_agent_md_snapshot",
          where:
            "repository_owner_name = $1 AND repository_name = $2 AND repository_workflow_run_id = $3",
          params: [owner, repository, runId],
          replica: "full",
        },
        parser: electricNumericParser,
        subscribe: true,
      },
    }),
  );
}

function createCodebaseProgressCollection({
  owner,
  repository,
  runId,
}: RepositoryAgentSnapshotScope) {
  return createCollection(
    electricCollectionOptions({
      id: `repository-agent-progress-${owner}-${repository}-${runId}`,
      schema: repositoryAgentCodebaseProgressRowSchema,
      getKey: (row: RepositoryAgentCodebaseProgressRow) =>
        `${row.repository_owner_name}/${row.repository_name}/${row.repository_workflow_run_id}/${row.codebase_name}`,
      startSync: false,
      gcTime: collectionGcTime,
      syncMode: "eager",
      shapeOptions: {
        url: electricShapeUrl,
        params: {
          table: "repository_agent_codebase_progress",
          where:
            "repository_owner_name = $1 AND repository_name = $2 AND repository_workflow_run_id = $3",
          params: [owner, repository, runId],
          replica: "full",
        },
        parser: electricNumericParser,
        subscribe: true,
      },
    }),
  );
}

function createRepositoryAgentEventCollection({
  owner,
  repository,
  runId,
  codebaseName,
}: RepositoryAgentCodebaseScope) {
  return createCollection(
    electricCollectionOptions({
      id: `repository-agent-events-${owner}-${repository}-${runId}-${codebaseName}`,
      schema: repositoryAgentEventSchema,
      getKey: (row: RepositoryAgentEvent) =>
        `${row.repository_owner_name}/${row.repository_name}/${row.repository_workflow_run_id}/${row.codebase_name}/${row.event_id}`,
      startSync: false,
      gcTime: collectionGcTime,
      // Event history is append-only and potentially unbounded, so prefer on-demand
      // subset loading instead of background full-history sync.
      syncMode: "on-demand",
      shapeOptions: {
        url: electricShapeUrl,
        params: {
          table: "repository_agent_event",
          where:
            "repository_owner_name = $1 AND repository_name = $2 AND repository_workflow_run_id = $3 AND codebase_name = $4",
          params: [owner, repository, runId, codebaseName],
          replica: "full",
        },
        subscribe: true,
      },
    }),
  );
}

export type RepositoryAgentSnapshotCollection = ReturnType<
  typeof createSnapshotCollection
>;
export type RepositoryAgentCodebaseProgressCollection = ReturnType<
  typeof createCodebaseProgressCollection
>;
export type RepositoryAgentEventCollection = ReturnType<
  typeof createRepositoryAgentEventCollection
>;

const snapshotCollections = new Map<
  string,
  RepositoryAgentSnapshotCollection
>();
const codebaseProgressCollections = new Map<
  string,
  RepositoryAgentCodebaseProgressCollection
>();
const eventCollections = new Map<string, RepositoryAgentEventCollection>();

export const getRepositoryAgentSnapshotCollection = (
  scope: RepositoryAgentSnapshotScope,
): RepositoryAgentSnapshotCollection => {
  const key = createScopeKey(scope);
  const existing = snapshotCollections.get(key);
  if (existing) {
    return existing;
  }

  const collection = createSnapshotCollection(scope);
  snapshotCollections.set(key, collection);
  return collection;
};

export const getRepositoryAgentCodebaseProgressCollection = (
  scope: RepositoryAgentSnapshotScope,
): RepositoryAgentCodebaseProgressCollection => {
  const key = createScopeKey(scope);
  const existing = codebaseProgressCollections.get(key);
  if (existing) {
    return existing;
  }

  const collection = createCodebaseProgressCollection(scope);
  codebaseProgressCollections.set(key, collection);
  return collection;
};

export const getRepositoryAgentEventCollection = (
  scope: RepositoryAgentCodebaseScope,
): RepositoryAgentEventCollection => {
  const key = createCodebaseScopeKey(scope);
  const existing = eventCollections.get(key);
  if (existing) {
    return existing;
  }

  const collection = createRepositoryAgentEventCollection(scope);
  eventCollections.set(key, collection);
  return collection;
};
