import {
  repositoryAgentSnapshotRowSchema,
  type ArtifactManifestEntry,
  type ArtifactPublicationError,
  type RepositoryAgentCodebaseProgressRow,
  type RepositoryAgentSnapshotMetadata,
  type RepositoryAgentSnapshotRow,
  type WorkflowStatistics,
} from "./schema";

export interface RepositoryAgentCodebaseState {
  codebaseName: string;
  progress: number | null;
}

// NOTE: status field does NOT exist in PostgreSQL repository_agent_md_snapshot table
// Use job.status from REST API (ParentWorkflowJobResponse) for status display
export interface ParsedRepositoryAgentSnapshot {
  repositoryWorkflowRunId: string;
  overallProgress: number;
  statistics: WorkflowStatistics | null;
  createdAt: string;
  updatedAt: string;
  latestEventAt?: string;
  repositoryActivityProgress: Record<string, number>;
  /** Changes when saved identity or its error changes. Refresh signal only. */
  artifactRefreshKey: string;
}

export interface RepositoryMarkdownArtifactFile {
  path: string;
  content: string;
}

export type RepositoryArtifactAvailability =
  | {
      availability: "available";
      commitSha: string;
      manifest: ArtifactManifestEntry[];
      publicationError: ArtifactPublicationError | null;
    }
  | {
      availability: "no_artifacts" | "pending" | "failed" | "unavailable";
      publicationError: ArtifactPublicationError | null;
    };

export function parseSnapshotRow(
  row: RepositoryAgentSnapshotRow,
): ParsedRepositoryAgentSnapshot {
  const parsed = repositoryAgentSnapshotRowSchema.parse(row);
  const overallProgress = normalizeProgress(parsed.overall_progress ?? null);

  return {
    repositoryWorkflowRunId: parsed.repository_workflow_run_id,
    overallProgress,
    statistics: parsed.statistics ?? null,
    createdAt: parsed.created_at,
    updatedAt: parsed.modified_at,
    latestEventAt: parsed.latest_event_at ?? undefined,
    repositoryActivityProgress: parsed.repository_activity_progress,
    artifactRefreshKey: JSON.stringify([
      parsed.artifact_commit_sha ?? null,
      parsed.artifact_publication_error ?? null,
    ]),
  };
}

/**
 * Converts snapshot metadata to a state where only "available" carries files.
 * A run with no snapshot row yet is pending while active and unavailable after.
 */
export function toRepositoryArtifactAvailability(
  metadata: RepositoryAgentSnapshotMetadata | null,
  isRunActive: boolean,
): RepositoryArtifactAvailability {
  if (!metadata) {
    return {
      availability: isRunActive ? "pending" : "unavailable",
      publicationError: null,
    };
  }

  const publicationError = metadata.artifact_publication_error;
  if (
    metadata.availability === "available" &&
    metadata.artifact_commit_sha &&
    metadata.artifact_manifest?.length
  ) {
    return {
      availability: "available",
      commitSha: metadata.artifact_commit_sha,
      manifest: metadata.artifact_manifest,
      publicationError,
    };
  }

  return {
    availability:
      metadata.availability === "available"
        ? "unavailable"
        : metadata.availability,
    publicationError,
  };
}

/**
 * Wraps text in a code span that its own backticks cannot close.
 */
function toMarkdownCodeSpan(value: string): string {
  const longestBacktickRun = Math.max(
    0,
    ...(value.match(/`+/g) ?? []).map((run) => run.length),
  );
  const delimiter = "`".repeat(longestBacktickRun + 1);
  return `${delimiter} ${value} ${delimiter}`;
}

/**
 * Joins files already read from the saved commit into one document. Each file
 * keeps its exact text under a heading naming its repository-relative path.
 */
export function assembleMarkdownArtifacts(
  repositoryName: string,
  commitSha: string,
  files: RepositoryMarkdownArtifactFile[],
): string {
  const sections = files.map(
    ({ path, content }) => `## ${toMarkdownCodeSpan(path)}\n\n${content}`,
  );
  return [
    `# AGENTS.md - ${repositoryName}`,
    `Commit: ${toMarkdownCodeSpan(commitSha)}`,
    ...sections,
  ].join("\n\n");
}

export function parseCodebaseProgressRows(
  rows: RepositoryAgentCodebaseProgressRow[],
): RepositoryAgentCodebaseState[] {
  return [...rows]
    .sort((left, right) =>
      left.codebase_name.localeCompare(right.codebase_name),
    )
    .map((row) => ({
      codebaseName: row.codebase_name,
      progress:
        typeof row.progress === "number"
          ? normalizeProgress(row.progress)
          : null,
    }));
}

function normalizeProgress(progress: number | null): number {
  if (typeof progress !== "number" || Number.isNaN(progress)) {
    return 0;
  }

  if (progress < 0) {
    return 0;
  }

  if (progress > 100) {
    return 100;
  }

  return progress;
}
