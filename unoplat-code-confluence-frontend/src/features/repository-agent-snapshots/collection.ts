import { createCollection } from "@tanstack/react-db";
import { electricCollectionOptions } from "@tanstack/electric-db-collection";

import { env } from "@/lib/env";

import {
  repositoryAgentSnapshotRowSchema,
  type RepositoryAgentSnapshotRow,
} from "./schema";

// Scope for querying by composite primary key (owner + repository + runId)
export interface RepositoryAgentSnapshotScope {
  owner: string;
  repository: string;
  runId: string;
}

const electricShapeUrl = `${env.electricBaseUrl.replace(/\/$/, "")}/v1/shape`;

// Create scope key for composite PK queries
const createScopeKey = ({
  owner,
  repository,
  runId,
}: RepositoryAgentSnapshotScope): string => `${owner}/${repository}/${runId}`;

// Create collection filtered by full composite primary key (owner + repo + runId)
function createCollectionForScope({
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
      // Let the first subscriber start syncing and GC after a short TTL
      startSync: false,
      gcTime: 1000 * 60 * 2,
      syncMode: "on-demand",
      shapeOptions: {
        url: electricShapeUrl,
        params: {
          table: "repository_agent_md_snapshot",
          where:
            "repository_owner_name = $1 AND repository_name = $2 AND repository_workflow_run_id = $3",
          params: [owner, repository, runId],
          replica: "full",
        },
        subscribe: true,
      },
    }),
  );
}

export type RepositoryAgentSnapshotCollection = ReturnType<
  typeof createCollectionForScope
>;

const snapshotCollections = new Map<
  string,
  RepositoryAgentSnapshotCollection
>();

// Get or create a collection for a specific workflow run
export const getRepositoryAgentSnapshotCollection = (
  scope: RepositoryAgentSnapshotScope,
): RepositoryAgentSnapshotCollection => {
  const key = createScopeKey(scope);
  const existing = snapshotCollections.get(key);
  if (existing) {
    return existing;
  }

  const collection = createCollectionForScope(scope);
  snapshotCollections.set(key, collection);
  return collection;
};
