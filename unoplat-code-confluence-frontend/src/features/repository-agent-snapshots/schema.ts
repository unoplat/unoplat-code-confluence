import { z } from "zod";

export const repositoryAgentEventSchema = z.object({
  repository_name: z.string(),
  repository_owner_name: z.string(),
  repository_workflow_run_id: z.string(),
  codebase_name: z.string(),
  event_id: z.number(),
  event: z.string(),
  phase: z.string(),
  message: z.string().optional().nullable(),
  tool_name: z.string().optional().nullable(),
  tool_call_id: z.string().optional().nullable(),
  tool_args: z.record(z.unknown()).optional().nullable(),
  tool_result_content: z.string().optional().nullable(),
  created_at: z.string(),
});

export type RepositoryAgentEvent = z.infer<typeof repositoryAgentEventSchema>;

export const repositoryAgentCodebaseProgressRowSchema = z.object({
  repository_name: z.string(),
  repository_owner_name: z.string(),
  repository_workflow_run_id: z.string(),
  codebase_name: z.string(),
  next_event_id: z.number(),
  latest_event_id: z.number().nullable().optional(),
  event_count: z.number(),
  progress: z.number().optional().nullable(),
  completed_namespaces: z.array(z.string()).default([]),
  latest_event_at: z.string().nullable().optional(),
  created_at: z.string(),
  modified_at: z.string(),
});

export type RepositoryAgentCodebaseProgressRow = z.infer<
  typeof repositoryAgentCodebaseProgressRowSchema
>;

// Nested schemas for agent_md_output.codebases structure

export const agentMdEngineeringWorkflowCommandSchema = z.object({
  command: z.string(),
  stage: z.enum(["install", "build", "dev", "test", "lint", "type_check"]),
  config_file: z.string(),
  working_directory: z.string().nullable().optional(),
});

export type AgentMdEngineeringWorkflowCommand = z.infer<
  typeof agentMdEngineeringWorkflowCommandSchema
>;

export const agentMdEngineeringWorkflowSchema = z.object({
  commands: z.array(agentMdEngineeringWorkflowCommandSchema).default([]),
});

export type AgentMdEngineeringWorkflow = z.infer<
  typeof agentMdEngineeringWorkflowSchema
>;

export const agentMdBusinessLogicSchema = z.object({
  description: z.string(),
  data_models: z.array(
    z.object({
      path: z.string(),
      responsibility: z.string().nullable(),
    }),
  ),
});

// Dependency Guide Entry schema
export const agentMdDependencyGuideEntrySchema = z.object({
  name: z.string(),
  purpose: z.string(),
  usage: z.string(),
});

export type AgentMdDependencyGuideEntry = z.infer<
  typeof agentMdDependencyGuideEntrySchema
>;

// Dependency Guide schema (collection)
export const agentMdDependencyGuideSchema = z.object({
  dependencies: z.array(agentMdDependencyGuideEntrySchema).default([]),
});

export type AgentMdDependencyGuide = z.infer<
  typeof agentMdDependencyGuideSchema
>;

export const agentMdInterfaceMatchPatternSchema = z
  .record(z.string(), z.array(z.string()).default([]))
  .default({});

export type AgentMdInterfaceMatchPattern = z.infer<
  typeof agentMdInterfaceMatchPatternSchema
>;

export const agentMdInterfaceConstructSchema = z.object({
  kind: z.string(),
  library: z.string(),
  match_pattern: agentMdInterfaceMatchPatternSchema,
});

export type AgentMdInterfaceConstruct = z.infer<
  typeof agentMdInterfaceConstructSchema
>;

export const agentMdAppInterfacesSchema = z.object({
  inbound_constructs: z.array(agentMdInterfaceConstructSchema).default([]),
  outbound_constructs: z.array(agentMdInterfaceConstructSchema).default([]),
  internal_constructs: z.array(agentMdInterfaceConstructSchema).default([]),
});

export type AgentMdAppInterfaces = z.infer<typeof agentMdAppInterfacesSchema>;

export const agentMdProgrammingLanguageMetadataSchema = z.object({
  primary_language: z.string(),
  package_manager: z.string(),
});

export type AgentMdProgrammingLanguageMetadata = z.infer<
  typeof agentMdProgrammingLanguageMetadataSchema
>;

export const agentMdCodebaseOutputSchema = z.object({
  codebase_name: z.string(),
  // Use .nullish() to accept both null (from PostgreSQL/Python None) and undefined (missing key)
  statistics: z.lazy(() => usageStatisticsSchema).nullish(),
  programming_language_metadata:
    agentMdProgrammingLanguageMetadataSchema.nullish(),
  engineering_workflow: agentMdEngineeringWorkflowSchema.nullish(),
  dependency_guide: agentMdDependencyGuideSchema.nullish(),
  business_logic_domain: agentMdBusinessLogicSchema.nullish(),
  app_interfaces: agentMdAppInterfacesSchema.nullish(),
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

// Main schema aligned with PostgreSQL repository_agent_md_snapshot table
// NOTE: status field does NOT exist in PostgreSQL - use job.status from REST API
export const repositoryAgentSnapshotRowSchema = z.object({
  // Primary key fields
  repository_name: z.string(),
  repository_owner_name: z.string(),
  repository_workflow_run_id: z.string(), // Part of composite PK - required

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
