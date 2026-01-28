import { z } from "zod";

/**
 * Tool configuration status values
 */
export const toolConfigStatusSchema = z.enum(["configured", "not_configured"]);

export type ToolConfigStatus = z.infer<typeof toolConfigStatusSchema>;

/**
 * Tool provider identifier values
 */
export const toolProviderSchema = z.enum(["exa"]);

export type ToolProvider = z.infer<typeof toolProviderSchema>;

/**
 * API response schema for tool configuration status
 */
export const toolConfigResponseSchema = z.object({
  provider: toolProviderSchema,
  status: toolConfigStatusSchema,
  configured_at: z.string().datetime({ offset: true }).nullish(),
});

export type ToolConfigResponse = z.infer<typeof toolConfigResponseSchema>;

/**
 * API response schema for listing all tool configs
 */
export const toolConfigListResponseSchema = z.object({
  tools: z.array(toolConfigResponseSchema),
});

export type ToolConfigListResponse = z.infer<
  typeof toolConfigListResponseSchema
>;
