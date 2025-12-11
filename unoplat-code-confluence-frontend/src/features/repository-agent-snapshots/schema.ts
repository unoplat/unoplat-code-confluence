import { z } from "zod";

export const repositoryAgentEventSchema = z.object({
  id: z.number(), // Backend returns numbers, not strings
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

// Nested schemas for agent_md_output.codebases structure
export const agentMdConfigFileSchema = z.object({
  path: z.string(),
  purpose: z.string(),
});

export type AgentMdConfigFile = z.infer<typeof agentMdConfigFileSchema>;

export const agentMdProjectConfigurationSchema = z.object({
  config_files: z.array(agentMdConfigFileSchema).default([]),
});

export type AgentMdProjectConfiguration = z.infer<
  typeof agentMdProjectConfigurationSchema
>;

export const agentMdDevelopmentCommandSchema = z.object({
  kind: z.string(),
  command: z.string(),
  description: z.string().optional(),
  config_files: z.array(z.string()).default([]),
});

export type AgentMdDevelopmentCommand = z.infer<
  typeof agentMdDevelopmentCommandSchema
>;

export const agentMdDevelopmentWorkflowSchema = z.object({
  commands: z.array(agentMdDevelopmentCommandSchema).default([]),
});

export type AgentMdDevelopmentWorkflow = z.infer<
  typeof agentMdDevelopmentWorkflowSchema
>;

export const agentMdCodebaseOutputSchema = z.object({
  codebase_name: z.string(),
  // Use .nullish() to accept both null (from PostgreSQL/Python None) and undefined (missing key)
  statistics: z.lazy(() => usageStatisticsSchema).nullish(),
  project_configuration: agentMdProjectConfigurationSchema.nullish(),
  development_workflow: agentMdDevelopmentWorkflowSchema.nullish(),
  business_logic_domain: z.string().nullish(),
});

export type AgentMdCodebaseOutput = z.infer<typeof agentMdCodebaseOutputSchema>;

// Agent MD output schema - codebases values are objects, not strings
// Electric SQL auto-parses JSONB columns
export const agentMdOutputSchema = z.object({
  repository: z.string().optional(),
  codebases: z.record(z.string(), agentMdCodebaseOutputSchema).default({}),
});

export type AgentMdOutputRecord = z.infer<typeof agentMdOutputSchema>;

export const usageStatisticsSchema = z.object({
  requests: z.number().default(0),
  tool_calls: z.number().default(0),
  input_tokens: z.number().default(0),
  output_tokens: z.number().default(0),
  cache_write_tokens: z.number().default(0),
  cache_read_tokens: z.number().default(0),
  total_tokens: z.number().default(0),
  estimated_cost_usd: z.number().nullable().optional(),
});

export type UsageStatistics = z.infer<typeof usageStatisticsSchema>;

export const workflowStatisticsSchema = z.object({
  total_requests: z.number().default(0),
  total_tool_calls: z.number().default(0),
  total_input_tokens: z.number().default(0),
  total_output_tokens: z.number().default(0),
  total_cache_write_tokens: z.number().default(0),
  total_cache_read_tokens: z.number().default(0),
  total_tokens: z.number().default(0),
  total_estimated_cost_usd: z.number().nullable().optional(),
  by_codebase: z.record(z.string(), usageStatisticsSchema).default({}),
});

export type WorkflowStatistics = z.infer<typeof workflowStatisticsSchema>;

// Schema for event_counters JSONB field (tracks next_id per codebase)
export const eventCounterEntrySchema = z.object({
  next_id: z.number(),
});

export type EventCounterEntry = z.infer<typeof eventCounterEntrySchema>;

// Schema for codebase_progress JSONB field (tracks progress and completed namespaces)
export const codebaseProgressEntrySchema = z.object({
  progress: z.number(),
  completed_namespaces: z.array(z.string()).default([]),
});

export type CodebaseProgressEntry = z.infer<typeof codebaseProgressEntrySchema>;

// Main schema aligned with PostgreSQL repository_agent_md_snapshot table
// NOTE: status field does NOT exist in PostgreSQL - use job.status from REST API
export const repositoryAgentSnapshotRowSchema = z.object({
  // Primary key fields
  repository_name: z.string(),
  repository_owner_name: z.string(),
  repository_workflow_run_id: z.string(), // Part of composite PK - required

  // JSONB fields with defaults in PostgreSQL (non-nullable)
  events: repositoryAgentEventsEnvelopeSchema.default({
    codebases: [],
  }),
  event_counters: z.record(z.string(), eventCounterEntrySchema).default({}),
  codebase_progress: z
    .record(z.string(), codebaseProgressEntrySchema)
    .default({}),
  agent_md_output: agentMdOutputSchema.default({
    codebases: {},
  }),

  // Optional JSONB field
  statistics: workflowStatisticsSchema.nullable().optional(),

  // Scalar fields - use coerce for wire protocol string→number conversion
  overall_progress: z.coerce.number().nullable().optional(), // Top-level progress (was inside events)
  latest_event_at: z.string().nullable().optional(), // ISO datetime of last event

  // Timestamps
  created_at: z.string(),
  modified_at: z.string(),
});

export type RepositoryAgentSnapshotRow = z.infer<
  typeof repositoryAgentSnapshotRowSchema
>;
