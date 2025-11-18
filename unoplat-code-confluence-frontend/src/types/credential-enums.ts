/**
 * Credential management enums and types
 * These match the backend schema in unoplat-code-confluence-commons/credential_enums.py
 */

/**
 * Defines the namespace/category for credentials
 */
export enum CredentialNamespace {
  REPOSITORY = "repository",
  MODEL = "MODEL",
  WEBHOOK = "WEBHOOK",
  IDENTITY = "IDENTITY",
}

/**
 * Defines the provider/platform for the credential
 */
export enum ProviderKey {
  GITHUB_OPEN = "github_open",
  GITHUB_ENTERPRISE = "github_enterprise",
  GITLAB_CE = "gitlab_ce",
  GITLAB_ENTERPRISE = "gitlab_enterprise",
  GOOGLE_AUTH = "google_oauth",
  GITHUB_AUTH = "github_oauth",
  MODEL_PROVIDER_AUTH = "model_provider_auth",
}

/**
 * Defines the type/kind of secret being stored
 */
export enum SecretKind {
  PAT = "pat",
  MODEL_API_KEY = "model_api_key",
  APP_PRIVATE_KEY = "app_private_key",
  APP_WEBHOOK_SECRET = "app_webhook_secret",
  APP_CLIENT_SECRET = "app_client_secret",
  APP_CLIENT_ID = "app_client_id",
  APP_INSTALLATION_TOKEN = "app_installation_token",
  OAUTH_ACCESS_TOKEN = "oauth_access_token",
  OAUTH_REFRESH_TOKEN = "oauth_refresh_token",
  OAUTH_ID_TOKEN = "oauth_id_token",
  JWT_SECRET = "jwt_secret",
}

/**
 * Parameters required for credential operations
 */
export interface CredentialParams {
  namespace: CredentialNamespace;
  provider_key: ProviderKey;
  secret_kind: SecretKind;
  /** Base URL for enterprise/self-hosted instances (optional) */
  url?: string;
}

/**
 * Parameters for token operations (ingest, update)
 */
export interface TokenOperationParams extends CredentialParams {
  token: string;
}
