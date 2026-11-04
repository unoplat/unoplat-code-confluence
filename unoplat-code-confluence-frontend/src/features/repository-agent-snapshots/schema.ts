import { z } from "zod";

// Safe activity metadata only. Generated bodies never belong in this schema:
// tool_args, tool_result_content and message are deliberately not projected.
export const repositoryAgentEventSchema = z.object({
  repository_name: z.string(),
  repository_owner_name: z.string(),
  repository_workflow_run_id: z.string(),
  codebase_name: z.string(),
  event_id: z.number(),
  event: z.string(),
  phase: z.string(),
  tool_name: z.string().optional().nullable(),
  tool_call_id: z.string().optional().nullable(),
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

export const repositoryActivityProgressSchema = z
  .record(z.string(), z.coerce.number())
  .default({});

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

  // Live refresh signals only. Availability and the manifest come from
  // GET /v1/repository-agent-snapshot, which validates stored identity. The
  // error stays unknown so a malformed value cannot stop live progress sync.
  artifact_commit_sha: z.string().nullable().optional(),
  artifact_publication_error: z.unknown(),

  repository_activity_progress: repositoryActivityProgressSchema,

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

export const artifactManifestEntrySchema = z.object({
  path: z.string().min(1),
  kind: z.enum(["markdown", "d2", "svg"]),
  scope: z.enum(["codebase", "repository"]),
  codebase_name: z.string().nullable(),
  byte_length: z.number().int().nonnegative(),
  sha256: z.string(),
});

export type ArtifactManifestEntry = z.infer<typeof artifactManifestEntrySchema>;

export const artifactPublicationErrorSchema = z.object({
  code: z.string(),
  stage: z.string(),
  message: z.string().max(512),
  retryable: z.boolean(),
});

export type ArtifactPublicationError = z.infer<
  typeof artifactPublicationErrorSchema
>;

// Response of GET /v1/repository-agent-snapshot. It holds no generated content.
export const repositoryAgentSnapshotMetadataSchema = z
  .object({
    repository_workflow_run_id: z.string(),
    availability: z.enum([
      "available",
      "no_artifacts",
      "pending",
      "failed",
      "unavailable",
    ]),
    artifact_commit_sha: z
      .string()
      .regex(/^[0-9a-f]{40}$/)
      .nullable(),
    artifact_manifest: z.array(artifactManifestEntrySchema).nullable(),
    artifact_publication_error: artifactPublicationErrorSchema.nullable(),
    repository_activity_progress: z.record(z.string(), z.number()),
    overall_progress: z.number().nullable(),
    statistics: workflowStatisticsSchema.nullable(),
  })
  .refine(
    (metadata) =>
      (metadata.availability === "available") ===
      (metadata.artifact_commit_sha !== null &&
        (metadata.artifact_manifest?.length ?? 0) > 0),
    { message: "Only available runs have a saved commit and files" },
  );

export type RepositoryAgentSnapshotMetadata = z.infer<
  typeof repositoryAgentSnapshotMetadataSchema
>;

export const artifactReadErrorCodeSchema = z.enum([
  "invalid_artifact_path",
  "run_not_found",
  "artifact_not_found",
  "artifact_identity_pending",
  "artifact_identity_unavailable",
  "artifact_identity_invalid",
  "artifact_integrity_failed",
  "artifact_missing_at_commit",
  "credentials_unavailable",
  "credentials_invalid",
  "provider_credentials_rejected",
  "provider_permission_denied",
  "provider_not_found",
  "provider_request_rejected",
  "provider_response_invalid",
  "provider_rate_limited",
  "provider_unavailable",
  "metadata_unavailable",
  "artifact_read_failed",
]);

export type ArtifactReadErrorCode = z.infer<typeof artifactReadErrorCodeSchema>;

export const artifactReadErrorResponseSchema = z.object({
  detail: z.object({
    code: artifactReadErrorCodeSchema,
    message: z.string().max(512),
    retryable: z.boolean(),
  }),
});
