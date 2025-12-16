import { useMemo } from "react";

import {
  repositoryAgentSnapshotRowSchema,
  type AgentMdCodebaseOutput,
  type AgentMdOutputRecord,
  type RepositoryAgentCodebaseProgress,
  type RepositoryAgentEvent,
  type RepositoryAgentSnapshotRow,
  type WorkflowStatistics,
} from "./schema";

export interface RepositoryAgentCodebaseState {
  codebaseName: string;
  progress: number | null;
  events: RepositoryAgentEvent[];
}

// NOTE: status field does NOT exist in PostgreSQL repository_agent_md_snapshot table
// Use job.status from REST API (ParentWorkflowJobResponse) for status display
export interface ParsedRepositoryAgentSnapshot {
  repositoryWorkflowRunId: string;
  overallProgress: number;
  codebases: RepositoryAgentCodebaseState[];
  markdownByCodebase: Record<string, AgentMdCodebaseOutput>;
  repositoryMarkdown?: string;
  statistics: WorkflowStatistics | null;
  createdAt: string;
  updatedAt: string;
  latestEventAt?: string;
}

export function useParsedSnapshot(
  row: RepositoryAgentSnapshotRow | undefined | null,
): ParsedRepositoryAgentSnapshot | null {
  return useMemo(() => (row ? parseSnapshotRow(row) : null), [row]);
}

export function parseSnapshotRow(
  row: RepositoryAgentSnapshotRow,
): ParsedRepositoryAgentSnapshot {
  const parsed = repositoryAgentSnapshotRowSchema.parse(row);

  const codebases = (parsed.events?.codebases ?? []).map((codebase) =>
    hydrateCodebase(codebase),
  );

  // Use top-level overall_progress (new PostgreSQL column) with fallback to events or computed average
  const baseOverall =
    typeof parsed.overall_progress === "number"
      ? parsed.overall_progress
      : typeof parsed.events?.overall_progress === "number"
        ? parsed.events?.overall_progress
        : null;
  const overallProgress = normalizeProgress(
    baseOverall ?? averageProgress(codebases),
  );

  const { markdownByCodebase, repositoryMarkdown } = parseAgentMdOutputs(
    parsed.agent_md_output,
  );

  return {
    repositoryWorkflowRunId: parsed.repository_workflow_run_id,
    overallProgress,
    codebases,
    markdownByCodebase,
    repositoryMarkdown,
    statistics: parsed.statistics ?? null,
    createdAt: parsed.created_at,
    updatedAt: parsed.modified_at,
    latestEventAt: parsed.latest_event_at ?? undefined,
  };
}

export function parseAgentMdOutputs(
  agentMdOutput: AgentMdOutputRecord | null | undefined,
): {
  markdownByCodebase: Record<string, AgentMdCodebaseOutput>;
  repositoryMarkdown?: string;
} {
  const markdownByCodebase: Record<string, AgentMdCodebaseOutput> = {};

  const codebasesEntries = agentMdOutput?.codebases
    ? Object.entries(agentMdOutput.codebases)
    : [];

  for (const [codebaseName, codebaseData] of codebasesEntries) {
    // Electric SQL auto-parses JSONB columns, so data is already an object
    if (isAgentMdCodebaseOutput(codebaseData)) {
      markdownByCodebase[codebaseName] = codebaseData;
      continue;
    }

    // Fallback for legacy stringified data (e.g., from SSE events)
    if (typeof codebaseData === "string") {
      try {
        const parsed = JSON.parse(codebaseData) as unknown;
        if (isAgentMdCodebaseOutput(parsed)) {
          markdownByCodebase[codebaseName] = parsed;
        }
      } catch (error) {
        console.error(
          `Failed to parse AgentMdCodebaseOutput for ${codebaseName}`,
          error,
        );
      }
    }
  }

  return {
    markdownByCodebase,
    repositoryMarkdown: agentMdOutput?.repository ?? undefined,
  };
}

// Type guard to check if data conforms to AgentMdCodebaseOutput structure
function isAgentMdCodebaseOutput(data: unknown): data is AgentMdCodebaseOutput {
  return (
    typeof data === "object" &&
    data !== null &&
    "project_configuration" in data
  );
}

export function parseAgentMdOutputsFromSnapshot(
  snapshot:
    | {
        repository?: string;
        codebases: Record<string, AgentMdCodebaseOutput | string>;
      }
    | null
    | undefined,
) {
  if (!snapshot) {
    return {
      markdownByCodebase: {} as Record<string, AgentMdCodebaseOutput>,
      repositoryMarkdown: undefined as string | undefined,
    };
  }

  // Cast to AgentMdOutputRecord since the actual parsing handles both types
  return parseAgentMdOutputs({
    repository: snapshot.repository,
    codebases: snapshot.codebases as AgentMdOutputRecord["codebases"],
  });
}

function hydrateCodebase(
  codebase: RepositoryAgentCodebaseProgress,
): RepositoryAgentCodebaseState {
  const events: RepositoryAgentEvent[] = Array.isArray(codebase.events)
    ? codebase.events
    : [];
  const numericProgress =
    typeof codebase.progress === "number" ? codebase.progress : null;

  return {
    codebaseName: codebase.codebase_name,
    progress: numericProgress,
    events,
  };
}

function averageProgress(
  codebases: RepositoryAgentCodebaseState[],
): number | null {
  const valid = codebases
    .map((entry) => entry.progress)
    .filter(
      (value): value is number =>
        typeof value === "number" && !Number.isNaN(value),
    );

  if (valid.length === 0) {
    return null;
  }

  const sum = valid.reduce((total, value) => total + value, 0);
  return sum / valid.length;
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
