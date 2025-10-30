import { z } from "zod";

export const repositoryAgentEventSchema = z.object({
  id: z.string(),
  event: z.string(),
  phase: z.string().optional().nullable(),
  message: z.string().optional().nullable(),
});

export type RepositoryAgentEvent = z.infer<typeof repositoryAgentEventSchema>;

export const repositoryAgentCodebaseProgressSchema = z.object({
  codebase_name: z.string(),
  progress: z.number().optional().nullable(),
  events: z.array(repositoryAgentEventSchema),
});

export type RepositoryAgentCodebaseProgress = z.infer<
  typeof repositoryAgentCodebaseProgressSchema
>;

export const repositoryAgentEventsEnvelopeSchema = z.object({
  repository_name: z.string().optional().nullable(),
  repository_workflow_run_id: z.string().optional().nullable(),
  overall_progress: z.number().optional().nullable(),
  codebases: z
    .array(repositoryAgentCodebaseProgressSchema)
    .optional()
    .default([]),
});

export type RepositoryAgentEventsEnvelope = z.infer<
  typeof repositoryAgentEventsEnvelopeSchema
>;

export const agentMdOutputSchema = z
  .object({
    repository: z.string().optional(),
    codebases: z.record(z.string(), z.string()).optional(),
  })
  .partial();

export type AgentMdOutputRecord = z.infer<typeof agentMdOutputSchema>;

export const repositoryAgentSnapshotRowSchema = z.object({
  repository_name: z.string(),
  repository_owner_name: z.string(),
  status: z.enum(["RUNNING", "COMPLETED", "ERROR"]),
  events: repositoryAgentEventsEnvelopeSchema.nullable().optional(),
  agent_md_output: agentMdOutputSchema.nullable().optional(),
  created_at: z.string(),
  modified_at: z.string(),
});

export type RepositoryAgentSnapshotRow = z.infer<
  typeof repositoryAgentSnapshotRowSchema
>;
