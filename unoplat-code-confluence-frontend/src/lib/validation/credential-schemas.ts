import { z } from "zod";
import {
  CredentialNamespace,
  ProviderKey,
  SecretKind,
} from "@/types/credential-enums";

/**
 * Base credential parameters schema
 */
export const credentialParamsSchema = z.object({
  namespace: z.nativeEnum(CredentialNamespace),
  provider_key: z.nativeEnum(ProviderKey),
  secret_kind: z.nativeEnum(SecretKind),
  url: z.string().url("Invalid URL format").optional(),
});

/**
 * Token form schema with validation for enterprise URL requirements
 */
export const tokenFormSchema = z
  .object({
    token: z.string().min(1, "Token is required"),
    provider_key: z.nativeEnum(ProviderKey),
    namespace: z
      .nativeEnum(CredentialNamespace)
      .default(CredentialNamespace.REPOSITORY),
    secret_kind: z.nativeEnum(SecretKind).default(SecretKind.PAT),
    url: z.string().url("Invalid URL format").optional(),
  })
  .refine(
    (data) => {
      // Enterprise providers require URL
      const needsUrl = [
        ProviderKey.GITHUB_ENTERPRISE,
        ProviderKey.GITLAB_ENTERPRISE,
      ].includes(data.provider_key);
      return !needsUrl || (needsUrl && data.url && data.url.length > 0);
    },
    {
      message: "Enterprise URL is required for enterprise providers",
      path: ["url"],
    },
  );

/**
 * Token update schema (same as token form)
 */
export const tokenUpdateSchema = tokenFormSchema;

/**
 * Token delete schema (no token or URL required, just identification params)
 */
export const tokenDeleteSchema = z.object({
  provider_key: z.nativeEnum(ProviderKey),
  namespace: z
    .nativeEnum(CredentialNamespace)
    .default(CredentialNamespace.REPOSITORY),
  secret_kind: z.nativeEnum(SecretKind).default(SecretKind.PAT),
});

/**
 * Repository request configuration schema
 */
export const repositoryRequestConfigSchema = z.object({
  repository_name: z.string().min(1, "Repository name is required"),
  repository_git_url: z.string().url("Invalid repository URL"),
  repository_owner_name: z.string().min(1, "Owner name is required"),
  repository_metadata: z
    .array(
      z.object({
        codebase_folder: z.string(),
        root_packages: z.array(z.string()).nullable().optional(),
        programming_language_metadata: z.object({
          language: z.string(),
          package_manager: z.string(),
          language_version: z.string().nullable().optional(),
          role: z.enum(["leaf", "aggregator", "NA"]).optional(),
          manifest_path: z.string().nullable().optional(),
          project_name: z.string().nullable().optional(),
        }),
        dependencies: z
          .array(
            z.object({
              name: z.string(),
              version: z.string(),
            }),
          )
          .optional(),
      }),
    )
    .nullable()
    .optional(),
  provider_key: z.nativeEnum(ProviderKey),
});

// Export TypeScript types derived from schemas
export type TokenFormData = z.infer<typeof tokenFormSchema>;
export type TokenDeleteData = z.infer<typeof tokenDeleteSchema>;
export type RepositoryRequestConfigData = z.infer<
  typeof repositoryRequestConfigSchema
>;
