import { useMemo } from 'react';
import type { AgentMdOutput } from '@/types/sse';

import {
  repositoryAgentSnapshotRowSchema,
  type AgentMdOutputRecord,
  type RepositoryAgentCodebaseProgress,
  type RepositoryAgentEvent,
  type RepositoryAgentSnapshotRow,
} from './schema';

export interface RepositoryAgentCodebaseState {
  codebaseName: string;
  progress: number | null;
  events: RepositoryAgentEvent[];
}

export interface ParsedRepositoryAgentSnapshot {
  status: RepositoryAgentSnapshotRow['status'];
  overallProgress: number;
  codebases: RepositoryAgentCodebaseState[];
  markdownByCodebase: Record<string, AgentMdOutput>;
  repositoryMarkdown?: string;
  createdAt: string;
  updatedAt: string;
}

export function useParsedSnapshot(row: RepositoryAgentSnapshotRow | undefined | null): ParsedRepositoryAgentSnapshot | null {
  return useMemo(() => (row ? parseSnapshotRow(row) : null), [row]);
}

export function parseSnapshotRow(row: RepositoryAgentSnapshotRow): ParsedRepositoryAgentSnapshot {
  const parsed = repositoryAgentSnapshotRowSchema.parse(row);

  const codebases = (parsed.events?.codebases ?? []).map((codebase) => hydrateCodebase(codebase));

  const baseOverall = typeof parsed.events?.overall_progress === 'number' ? parsed.events?.overall_progress : null;
  const overallProgress = normalizeProgress(baseOverall ?? averageProgress(codebases));

  const { markdownByCodebase, repositoryMarkdown } = parseAgentMdOutputs(parsed.agent_md_output);

  return {
    status: parsed.status,
    overallProgress,
    codebases,
    markdownByCodebase,
    repositoryMarkdown,
    createdAt: parsed.created_at,
    updatedAt: parsed.modified_at,
  };
}

export function parseAgentMdOutputs(agentMdOutput: AgentMdOutputRecord | null | undefined): {
  markdownByCodebase: Record<string, AgentMdOutput>;
  repositoryMarkdown?: string;
} {
  const markdownByCodebase: Record<string, AgentMdOutput> = {};

  const codebasesEntries = agentMdOutput?.codebases ? Object.entries(agentMdOutput.codebases) : [];
  for (const [codebaseName, jsonString] of codebasesEntries) {
    if (typeof jsonString !== 'string') {
      continue;
    }

    try {
      markdownByCodebase[codebaseName] = JSON.parse(jsonString) as AgentMdOutput;
    } catch (error) {
      console.error(`Failed to parse AgentMdOutput for ${codebaseName}`, error);
    }
  }

  return {
    markdownByCodebase,
    repositoryMarkdown: agentMdOutput?.repository ?? undefined,
  };
}

export function parseAgentMdOutputsFromSnapshot(snapshot: {
  repository?: string;
  codebases: Record<string, string>;
} | null | undefined) {
  if (!snapshot) {
    return {
      markdownByCodebase: {} as Record<string, AgentMdOutput>,
      repositoryMarkdown: undefined as string | undefined,
    };
  }

  return parseAgentMdOutputs({
    repository: snapshot.repository,
    codebases: snapshot.codebases,
  });
}

function hydrateCodebase(codebase: RepositoryAgentCodebaseProgress): RepositoryAgentCodebaseState {
  const events: RepositoryAgentEvent[] = Array.isArray(codebase.events) ? codebase.events : [];
  const numericProgress = typeof codebase.progress === 'number' ? codebase.progress : null;

  return {
    codebaseName: codebase.codebase_name,
    progress: numericProgress,
    events,
  };
}

function averageProgress(codebases: RepositoryAgentCodebaseState[]): number | null {
  const valid = codebases
    .map((entry) => entry.progress)
    .filter((value): value is number => typeof value === 'number' && !Number.isNaN(value));

  if (valid.length === 0) {
    return null;
  }

  const sum = valid.reduce((total, value) => total + value, 0);
  return sum / valid.length;
}

function normalizeProgress(progress: number | null): number {
  if (typeof progress !== 'number' || Number.isNaN(progress)) {
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
