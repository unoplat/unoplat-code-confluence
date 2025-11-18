import {
  CredentialNamespace,
  ProviderKey,
  SecretKind,
  CredentialParams,
} from "@/types/credential-enums";

/**
 * Default secret kind for each credential namespace
 */
export const DEFAULT_SECRET_KIND_BY_NAMESPACE: Record<
  CredentialNamespace,
  SecretKind
> = {
  [CredentialNamespace.REPOSITORY]: SecretKind.PAT,
  [CredentialNamespace.MODEL]: SecretKind.MODEL_API_KEY,
  [CredentialNamespace.WEBHOOK]: SecretKind.APP_WEBHOOK_SECRET,
  [CredentialNamespace.IDENTITY]: SecretKind.OAUTH_ACCESS_TOKEN,
};

/**
 * List of enterprise providers that require URL
 */
export const ENTERPRISE_PROVIDERS: ProviderKey[] = [
  ProviderKey.GITHUB_ENTERPRISE,
  ProviderKey.GITLAB_ENTERPRISE,
];

/**
 * Provider display names
 */
export const PROVIDER_DISPLAY_NAMES: Record<ProviderKey, string> = {
  [ProviderKey.GITHUB_OPEN]: "GitHub",
  [ProviderKey.GITHUB_ENTERPRISE]: "GitHub Enterprise",
  [ProviderKey.GITLAB_CE]: "GitLab",
  [ProviderKey.GITLAB_ENTERPRISE]: "GitLab Enterprise",
  [ProviderKey.GOOGLE_AUTH]: "Google OAuth",
  [ProviderKey.GITHUB_AUTH]: "GitHub OAuth",
  [ProviderKey.MODEL_PROVIDER_AUTH]: "Model Provider",
};

/**
 * Secret kind display names
 */
export const SECRET_KIND_DISPLAY_NAMES: Record<SecretKind, string> = {
  [SecretKind.PAT]: "Personal Access Token",
  [SecretKind.MODEL_API_KEY]: "Model API Key",
  [SecretKind.APP_PRIVATE_KEY]: "App Private Key",
  [SecretKind.APP_WEBHOOK_SECRET]: "Webhook Secret",
  [SecretKind.APP_CLIENT_SECRET]: "Client Secret",
  [SecretKind.APP_CLIENT_ID]: "Client ID",
  [SecretKind.APP_INSTALLATION_TOKEN]: "Installation Token",
  [SecretKind.OAUTH_ACCESS_TOKEN]: "OAuth Access Token",
  [SecretKind.OAUTH_REFRESH_TOKEN]: "OAuth Refresh Token",
  [SecretKind.OAUTH_ID_TOKEN]: "OAuth ID Token",
  [SecretKind.JWT_SECRET]: "JWT Secret",
};

/**
 * Namespace display names
 */
export const NAMESPACE_DISPLAY_NAMES: Record<CredentialNamespace, string> = {
  [CredentialNamespace.REPOSITORY]: "Repository",
  [CredentialNamespace.MODEL]: "Model",
  [CredentialNamespace.WEBHOOK]: "Webhook",
  [CredentialNamespace.IDENTITY]: "Identity",
};

/**
 * Available secret kinds per namespace
 */
export const SECRET_KINDS_BY_NAMESPACE: Record<
  CredentialNamespace,
  SecretKind[]
> = {
  [CredentialNamespace.REPOSITORY]: [
    SecretKind.PAT,
    SecretKind.APP_PRIVATE_KEY,
    SecretKind.APP_INSTALLATION_TOKEN,
  ],
  [CredentialNamespace.MODEL]: [SecretKind.MODEL_API_KEY],
  [CredentialNamespace.WEBHOOK]: [
    SecretKind.APP_WEBHOOK_SECRET,
    SecretKind.APP_CLIENT_SECRET,
  ],
  [CredentialNamespace.IDENTITY]: [
    SecretKind.OAUTH_ACCESS_TOKEN,
    SecretKind.OAUTH_REFRESH_TOKEN,
    SecretKind.OAUTH_ID_TOKEN,
    SecretKind.JWT_SECRET,
  ],
};

/**
 * Available providers per namespace
 */
export const PROVIDERS_BY_NAMESPACE: Record<CredentialNamespace, ProviderKey[]> =
  {
    [CredentialNamespace.REPOSITORY]: [
      ProviderKey.GITHUB_OPEN,
      ProviderKey.GITHUB_ENTERPRISE,
      ProviderKey.GITLAB_CE,
      ProviderKey.GITLAB_ENTERPRISE,
    ],
    [CredentialNamespace.MODEL]: [ProviderKey.MODEL_PROVIDER_AUTH],
    [CredentialNamespace.WEBHOOK]: [
      ProviderKey.GITHUB_OPEN,
      ProviderKey.GITHUB_ENTERPRISE,
      ProviderKey.GITLAB_CE,
      ProviderKey.GITLAB_ENTERPRISE,
    ],
    [CredentialNamespace.IDENTITY]: [
      ProviderKey.GOOGLE_AUTH,
      ProviderKey.GITHUB_AUTH,
    ],
  };

/**
 * Default credential namespace for the application
 */
export const DEFAULT_CREDENTIAL_NAMESPACE = CredentialNamespace.REPOSITORY;

/**
 * Default provider key for repository operations
 */
export const DEFAULT_REPOSITORY_PROVIDER = ProviderKey.GITHUB_OPEN;

/**
 * Default credential parameters for repository-scoped GitHub PAT operations
 * Used for submit/update/delete flows until UI supports multi-provider selection
 */
export const DEFAULT_REPOSITORY_CREDENTIAL_PARAMS: Readonly<
  Omit<CredentialParams, "url">
> = {
  namespace: DEFAULT_CREDENTIAL_NAMESPACE,
  provider_key: DEFAULT_REPOSITORY_PROVIDER,
  secret_kind:
    DEFAULT_SECRET_KIND_BY_NAMESPACE[DEFAULT_CREDENTIAL_NAMESPACE],
};
