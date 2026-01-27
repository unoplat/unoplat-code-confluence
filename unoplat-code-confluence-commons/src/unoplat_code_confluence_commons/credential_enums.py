from enum import Enum


class CredentialNamespace(str, Enum):
    REPOSITORY = "repository"
    MODEL = "MODEL"
    WEBHOOK = "WEBHOOK"
    IDENTITY = "IDENTITY"
    TOOL = "tool"  # For Tool/MCP configurations (e.g., Exa search API)


class ProviderKey(str, Enum):
    GITHUB_OPEN = "github_open"
    GITHUB_ENTERPRISE = "github_enterprise"
    GITLAB_CE = "gitlab_ce"
    GITLAB_ENTERPRISE = "gitlab_enterprise"
    GOOGLE_AUTH = "google_oauth"
    GITHUB_AUTH = "github_oauth"
    MODEL_PROVIDER_AUTH = "model_provider_auth"
    EXA = "exa"  # Exa search API provider for tool/MCP configurations


class SecretKind(str, Enum):
    PAT = "pat"

    MODEL_API_KEY = "model_api_key"
    TOOL_API_KEY = "tool_api_key"  # Generic API key for tools/MCPs (e.g., Exa)

    APP_PRIVATE_KEY = "app_private_key"
    APP_WEBHOOK_SECRET = "app_webhook_secret"
    APP_CLIENT_SECRET = "app_client_secret"
    APP_CLIENT_ID = "app_client_id"
    APP_INSTALLATION_TOKEN = "app_installation_token"

    OAUTH_ACCESS_TOKEN = "oauth_access_token"
    OAUTH_REFRESH_TOKEN = "oauth_refresh_token"
    OAUTH_ID_TOKEN = "oauth_id_token"

    JWT_SECRET = "jwt_secret"
