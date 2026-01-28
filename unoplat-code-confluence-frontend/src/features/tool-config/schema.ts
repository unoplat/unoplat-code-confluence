import { z } from "zod";

/**
 * Validation schema for Exa API key form input
 * Used with TanStack Form for form validation
 */
export const exaApiKeySchema = z.object({
  api_key: z.string().min(1, "API key is required").trim(),
});

export type ExaApiKeyFormValues = z.infer<typeof exaApiKeySchema>;
