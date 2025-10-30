import { createCollection } from "@tanstack/react-db";
import { electricCollectionOptions } from "@tanstack/electric-db-collection";

import { env } from "@/lib/env";

import {
  repositoryAgentSnapshotRowSchema,
  type RepositoryAgentSnapshotRow,
} from "./schema";

export interface RepositoryAgentSnapshotScope {
  owner: string;
  repository: string;
}

const electricShapeUrl = `${env.electricBaseUrl.replace(/\/$/, "")}/v1/shape`;

const createScopeKey = ({
  owner,
  repository,
}: RepositoryAgentSnapshotScope): string => `${owner}/${repository}`;

function createCollectionForScope({
  owner,
  repository,
}: RepositoryAgentSnapshotScope) {
  return createCollection(
    electricCollectionOptions({
      id: `repository-agent-snapshots-${owner}-${repository}`,
      schema: repositoryAgentSnapshotRowSchema,
      getKey: (row: RepositoryAgentSnapshotRow) =>
        `${row.repository_owner_name}/${row.repository_name}`,
      shapeOptions: {
        url: electricShapeUrl,
        params: {
          table: "repository_agent_md_snapshot",
          where: "repository_owner_name = $1 AND repository_name = $2",
          params: [owner, repository],
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

export const destroyRepositoryAgentSnapshotCollection = async (
  scope: RepositoryAgentSnapshotScope,
): Promise<void> => {
  const key = createScopeKey(scope);
  const collection = snapshotCollections.get(key);
  snapshotCollections.delete(key);
  await collection?.cleanup();
};
