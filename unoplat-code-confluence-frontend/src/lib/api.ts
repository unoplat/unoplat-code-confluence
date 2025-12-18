import axios, { AxiosResponse, AxiosError } from "axios";
import { apiClient, queryEngineClient } from "./api/clients";
import {
  FlagResponse,
  GitHubRepoSummary,
  PaginatedResponse,
  RepositoryRequestConfiguration,
  GitHubRepoResponseConfiguration,
  IngestedRepository,
  IngestedRepositoriesResponse,
  RefreshRepositoryResponse,
  CodebaseMetadataResponse,
  ParentWorkflowJobListResponse,
  GithubRepoStatus,
  RepositoryWorkflowOperation,
} from "@/types";
import { CredentialParams, ProviderKey } from "@/types/credential-enums";
import { providerCatalogSchema } from "@/features/model-config/provider-schema";
import {
  ModelProviderDefinition,
  ProviderCatalogRecord,
} from "@/features/model-config/types";

// Re-export types from '../types' for consumers
export type {
  FlagResponse,
  GitHubRepoSummary,
  PaginatedResponse,
  IngestedRepository,
  IngestedRepositoriesResponse,
  RefreshRepositoryResponse,
};

// Re-export provider API functions
export {
  fetchProvidersApi,
  submitProviderForm,
} from "@/lib/api/repository-provider-api";

// Re-export repositories API functions
export { fetchRepositoriesApi } from "@/lib/api/repositories-api";

/**
 * API Services
 *
 * Collection of API service functions for backend communication.
 */

// Axios clients are imported from ./api/clients.ts to avoid duplication

// Response interface
export interface ApiResponse {
  success: boolean;
  message?: string;
}

// Error interface for consistent error handling
export interface ApiError {
  message: string;
  statusCode?: number;
  details?: unknown;
  isAxiosError: boolean;
}

/**
 * Generic error handler for API errors
 *
 * @param error - Error from API call
 * @returns Standardized API error object
 */
export const handleApiError = (error: unknown): ApiError => {
  console.error("API Error:", error);

  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiResponse>;
    return {
      message:
        axiosError.response?.data?.message ||
        axiosError.message ||
        "Unknown API error",
      statusCode: axiosError.response?.status,
      details: axiosError.response?.data,
      isAxiosError: true,
    };
  }

  return {
    message: error instanceof Error ? error.message : "Unknown error",
    isAxiosError: false,
    details: error,
  };
};

/**
 * Submit GitHub PAT token to the backend
 *
 * @param token - GitHub Personal Access Token
 * @param params - Credential parameters (namespace, provider_key, secret_kind, url)
 * @returns Promise with the response data
 */
export const submitGitHubToken = async (
  token: string,
  params: CredentialParams,
): Promise<ApiResponse> => {
  try {
    // Build query parameters
    const queryParams = {
      namespace: params.namespace,
      provider_key: params.provider_key,
      secret_kind: params.secret_kind,
      ...(params.url && { url: params.url }),
    };

    // Pass null as data and override Content-Type header
    const response: AxiosResponse<ApiResponse> = await apiClient.post(
      "/ingest-token",
      null,
      {
        params: queryParams,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": undefined, // Prevent sending default Content-Type
        },
      },
    );

    return response.data;
  } catch (error: unknown) {
    const apiError = handleApiError(error);

    // If we have a valid response from the server, return it
    // This might occur for non-2xx status codes that still carry a meaningful API response body
    if (
      apiError.isAxiosError &&
      apiError.statusCode &&
      apiError.details &&
      typeof apiError.details === "object" &&
      apiError.details !== null &&
      "success" in apiError.details
    ) {
      // Attempt to cast details to ApiResponse if it looks like one
      return apiError.details as ApiResponse;
    }

    // Otherwise, throw the standardized error object for further handling upstream
    throw apiError;
  }
};

// Add the following interface above the fetchGitHubRepositories function

/**
 * Fetch GitHub repositories from the backend
 *
 * @param page - Page number for pagination
 * @param perPage - Number of items per page
 * @param providerKey - Repository provider key (required)
 * @param filterValues - Optional filter values
 * @param cursor - Optional cursor for pagination
 * @returns Promise with paginated GitHub repositories
 */
interface FetchGitHubRepositoriesParams {
  perPage: number;
  providerKey: ProviderKey;
  filterValues?: Record<string, string | string[] | null>;
  cursor?: string;
}

export const fetchGitHubRepositories = async ({
  perPage,
  providerKey,
  filterValues,
  cursor,
}: FetchGitHubRepositoriesParams): Promise<
  PaginatedResponse<GitHubRepoSummary>
> => {
  try {
    const params: Record<string, string | number> = {
      per_page: perPage,
      provider_key: providerKey,
    };

    if (filterValues) {
      params.filterValues = JSON.stringify(filterValues);
    }

    if (cursor) {
      params.cursor = cursor;
    }

    const response: AxiosResponse<PaginatedResponse<GitHubRepoSummary>> =
      await apiClient.get("/repos", { params });
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

/**
 * Submit selected repositories for ingestion
 *
 * @param repositoryConfig - Repository configuration payload
 * @returns Promise with the response data
 */
export const submitRepositoryConfig = async (
  repositoryConfig: RepositoryRequestConfiguration,
): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.post(
      "/start-ingestion",
      repositoryConfig,
    );
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

/**
 * Update GitHub PAT token in the backend
 *
 * @param token - GitHub Personal Access Token
 * @param params - Credential parameters (namespace, provider_key, secret_kind, url)
 * @returns Promise with the response data
 */
export const updateGitHubToken = async (
  token: string,
  params: CredentialParams,
): Promise<ApiResponse> => {
  try {
    // Build query parameters
    const queryParams = {
      namespace: params.namespace,
      provider_key: params.provider_key,
      secret_kind: params.secret_kind,
      ...(params.url && { url: params.url }),
    };

    // Pass null as data and override Content-Type header
    const response: AxiosResponse<ApiResponse> = await apiClient.put(
      "/update-token",
      null,
      {
        params: queryParams,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": undefined, // Prevent sending default Content-Type
        },
      },
    );

    return response.data;
  } catch (error: unknown) {
    const apiError = handleApiError(error);

    // If we have a valid response from the server, return it
    // This might occur for non-2xx status codes that still carry a meaningful API response body
    if (
      apiError.isAxiosError &&
      apiError.statusCode &&
      apiError.details &&
      typeof apiError.details === "object" &&
      apiError.details !== null &&
      "success" in apiError.details
    ) {
      // Attempt to cast details to ApiResponse if it looks like one
      return apiError.details as ApiResponse;
    }

    // Otherwise, throw the standardized error object for further handling upstream
    throw apiError;
  }
};

/**
 * Delete GitHub PAT token from the backend
 *
 * @param params - Credential parameters (namespace, provider_key, secret_kind)
 * @returns Promise with the response data
 */
export const deleteGitHubToken = async (
  params: Omit<CredentialParams, "url">,
): Promise<ApiResponse> => {
  try {
    // Build query parameters
    const queryParams = {
      namespace: params.namespace,
      provider_key: params.provider_key,
      secret_kind: params.secret_kind,
    };

    const response: AxiosResponse<ApiResponse> = await apiClient.delete(
      "/delete-token",
      { params: queryParams },
    );
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

export const getFlagStatus = async (
  flagName: string,
): Promise<FlagResponse> => {
  try {
    const response: AxiosResponse<FlagResponse> = await apiClient.get(
      `/flags/${flagName}`,
    );
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiResponse>;
      if (axiosError.response?.status === 404) {
        return { status: false };
      }
      // Add errorCode for connection errors
      if (!axiosError.response) {
        return { status: true, errorCode: 503 };
      }
    }

    throw handleApiError(error);
  }
};

/**
 * Create repository data (configuration) in the backend
 * @param config - Repository configuration payload
 * @returns Promise with the response data
 */
export const createRepositoryData = async (
  config: RepositoryRequestConfiguration,
): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.post(
      "/repository-data",
      config,
    );
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

/**
 * Commented as of now
 * Update repository data (configuration) in the backend
 * @param config - Repository configuration payload
 * @returns Promise with the response data
 */
// export const updateRepositoryData = async (
//   config: GitHubRepoRequestConfiguration
// ): Promise<ApiResponse> => {
//   try {
//     const response: AxiosResponse<ApiResponse> = await apiClient.put('/repository-data', config);
//     return response.data;
//   } catch (error: unknown) {
//     throw handleApiError(error);
//   }
// };

/**
 * Get repository configuration from the backend
 * @param repositoryName - The name of the repository
 * @returns Promise with the repository configuration or null if not found
 */
export const getRepositoryConfig = async (
  repositoryName: string,
  ownerName: string,
): Promise<GitHubRepoResponseConfiguration | null> => {
  try {
    const response: AxiosResponse<GitHubRepoResponseConfiguration> =
      await apiClient.get("/repository-data", {
        params: {
          repository_name: repositoryName,
          repository_owner_name: ownerName,
        },
      });
    return response.data;
  } catch (error: unknown) {
    // If it's a 404 error, return null instead of throwing an error
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw handleApiError(error);
  }
};

/**
 * GitHub user type response
 */
export interface GitHubUser {
  login: string;
  name: string | null;
  avatar_url: string;
  /** User email address (nullable) */
  email?: string | null;
}

/**
 * Fetch the authenticated GitHub user using the stored PAT token
 *
 * @param providerKey - Repository provider key (required)
 * @returns Promise with the GitHub user data
 */
export async function fetchGitHubUser(
  providerKey: ProviderKey,
): Promise<GitHubUser> {
  // Get the token from backend
  const response: AxiosResponse<GitHubUser> = await apiClient.get(
    "/user-details",
    {
      params: { provider_key: providerKey },
    },
  );
  return response.data;
}

/**
 * Fetch all parent workflow jobs
 *
 * @returns Promise with the parent workflow jobs list response
 */
export const getParentWorkflowJobs =
  async (): Promise<ParentWorkflowJobListResponse> => {
    console.log("[API] getParentWorkflowJobs called");
    try {
      const response: AxiosResponse<ParentWorkflowJobListResponse> =
        await apiClient.get("/parent-workflow-jobs");
      console.log("[API] getParentWorkflowJobs response data:", response.data);
      return response.data;
    } catch (error: unknown) {
      throw handleApiError(error);
    }
  };

/**
 * Get repository status for a specific workflow run
 *
 * @param repositoryName - The name of the repository
 * @param repositoryOwnerName - The name of the repository owner
 * @param workflowRunId - The workflow run ID to fetch status for
 * @returns Promise with the repository status response
 */
export const getRepositoryStatus = async (
  repositoryName: string,
  repositoryOwnerName: string,
  workflowRunId: string,
): Promise<GithubRepoStatus> => {
  console.log("[API] getRepositoryStatus called with params:", {
    repositoryName,
    repositoryOwnerName,
    workflowRunId,
  });
  try {
    const params = {
      repository_name: repositoryName,
      repository_owner_name: repositoryOwnerName,
      workflow_run_id: workflowRunId,
    };
    console.log("[API] getRepositoryStatus params:", params);
    const response: AxiosResponse<GithubRepoStatus> = await apiClient.get(
      "/repository-status",
      { params },
    );
    console.log("[API] getRepositoryStatus response data:", response.data);
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

/**
 * GitHub Issue submission request interface based on API schema
 */
export interface GithubIssueSubmissionRequest {
  repository_name: string;
  repository_owner_name: string;
  parent_workflow_run_id: string;
  error_type: string;
  codebase_folder?: string | null;
  codebase_workflow_run_id?: string | null;
  error_message_body: string;
  /** Operation type for generating contextual GitHub issue titles */
  operation_type: RepositoryWorkflowOperation;
}

/**
 * Issue tracking response interface based on API schema
 */
export interface IssueTracking {
  issue_id?: string | null;
  issue_number?: number | null;
  issue_url?: string | null;
  issue_status?: string | null;
  created_at?: string | null;
}

/**
 * Submit feedback for a workflow error to create a GitHub issue
 *
 * @param requestData - GitHub issue submission data
 * @returns Promise with the issue tracking response
 */
export const submitFeedback = async (
  requestData: GithubIssueSubmissionRequest,
): Promise<IssueTracking> => {
  console.log("[API] submitFeedback request data:", requestData);
  try {
    const response: AxiosResponse<IssueTracking> = await apiClient.post(
      "/code-confluence/issues",
      requestData,
    );
    console.log("[API] submitFeedback response data:", response.data);
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

export async function getCodebaseMetadata(
  repositoryOwnerName: string,
  repositoryName: string,
): Promise<CodebaseMetadataResponse> {
  try {
    const params = {
      repository_owner_name: repositoryOwnerName,
      repository_name: repositoryName,
    } as Record<string, string>;
    const res: AxiosResponse<CodebaseMetadataResponse> = await apiClient.get(
      "/codebase-metadata",
      { params },
    );
    return res.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
}

/**
 * Fetch ingested repositories from the backend
 *
 * @returns Promise with ingested repositories data
 */
export const getIngestedRepositories =
  async (): Promise<IngestedRepositoriesResponse> => {
    try {
      const response: AxiosResponse<IngestedRepositoriesResponse> =
        await apiClient.get("/get/ingestedRepositories");
      return response.data;
    } catch (error: unknown) {
      throw handleApiError(error);
    }
  };

/**
 * Refresh an ingested repository
 *
 * @param repository - Repository object containing name and owner
 * @returns Promise with the refresh repository response
 */
export const refreshRepository = async (
  repository: IngestedRepository,
): Promise<RefreshRepositoryResponse> => {
  try {
    const response: AxiosResponse<RefreshRepositoryResponse> =
      await apiClient.post("/refresh-repository", repository);
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

/**
 * Delete an ingested repository
 *
 * @param repository - Repository object containing name and owner
 * @returns Promise with the response data
 */
export const deleteRepository = async (
  repository: IngestedRepository,
): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.delete(
      "/delete-repository",
      { data: repository },
    );
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

export type RepoAgentSnapshotStatus = "RUNNING" | "COMPLETED" | "ERROR";

export interface RepositoryWorkflowRunResponse {
  repository_workflow_run_id: string;
}

export async function startRepositoryAgentRun(
  ownerName: string,
  repoName: string,
): Promise<RepositoryWorkflowRunResponse> {
  try {
    const params = {
      owner_name: ownerName,
      repo_name: repoName,
    };

    const response: AxiosResponse<RepositoryWorkflowRunResponse> =
      await queryEngineClient.get("/v1/codebase-agent-rules", {
        params,
      });

    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
}

interface RepositoryAgentSnapshotResponse {
  status: RepoAgentSnapshotStatus;
  agent_md_output: {
    repository?: string;
    codebases?: Record<string, string>;
  } | null;
}

/**
 * Repository agent snapshot normalized for frontend consumption.
 */
export interface RepositoryAgentSnapshot {
  status: RepoAgentSnapshotStatus;
  repository?: string;
  codebases: Record<string, string>; // codebase_name -> JSON string of AgentMdCodebaseOutput
}

/**
 * Fetch existing repository agent snapshot from the backend
 *
 * @param ownerName - Repository owner name
 * @param repoName - Repository name
 * @returns Promise with repository agent snapshot or null if not found
 */
export async function getRepositoryAgentSnapshot(
  ownerName: string,
  repoName: string,
): Promise<RepositoryAgentSnapshot | null> {
  try {
    const params = {
      owner_name: ownerName,
      repo_name: repoName,
    };
    const response: AxiosResponse<RepositoryAgentSnapshotResponse> =
      await queryEngineClient.get("/v1/repository-agent-snapshot", {
        params,
      });
    const { status, agent_md_output } = response.data;

    return {
      status,
      repository: agent_md_output?.repository,
      codebases: agent_md_output?.codebases ?? {},
    };
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw handleApiError(error);
  }
}

// Model Configuration API

/**
 * Response from the model configuration endpoint
 */
export interface ModelConfigResponse {
  provider_key: string;
  model_name: string;
  provider_name?: string | null;
  provider_kind?: string;
  base_url?: string | null;
  profile_key?: string | null;
  extra_config?: Record<string, unknown>;
  temperature?: number | null;
  top_p?: number | null;
  max_tokens?: number | null;
  has_api_key: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Request body for saving model provider configuration
 */
export interface SaveModelConfigRequest {
  provider_key: string;
  model_name: string;
  model_api_key?: string; // API key for the provider (goes in header)
  [key: string]: unknown; // Additional provider-specific fields
}

/**
 * Fetch model providers from the query engine
 * Backend returns a record/object with provider keys as keys
 * We transform it to an array with backfilled provider_key for frontend use
 *
 * @returns Promise with array of model provider definitions
 */
export const getModelProviders = async (): Promise<
  ModelProviderDefinition[]
> => {
  try {
    const response: AxiosResponse<ProviderCatalogRecord> =
      await queryEngineClient.get("/v1/providers");

    // Parse the record response
    const providersRecord = providerCatalogSchema.parse(response.data);

    // Transform to array with backfilled provider_key
    const providersArray = Object.entries(providersRecord).map(
      ([key, provider]) => ({
        ...provider,
        provider_key: key, // Backfill the provider_key from the record key
      }),
    ) as ModelProviderDefinition[];

    return providersArray;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

/**
 * Fetch existing model configuration from the query engine
 *
 * @returns Promise with the model configuration or null if not configured
 */
export const getModelConfig = async (): Promise<ModelConfigResponse | null> => {
  try {
    const response: AxiosResponse<ModelConfigResponse> =
      await queryEngineClient.get("/v1/model-config");
    return response.data;
  } catch (error: unknown) {
    // Return null if no config exists (404)
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw handleApiError(error);
  }
};

/**
 * Save model provider configuration to the query engine
 *
 * @param config - Configuration data including provider key, model name, and provider-specific fields
 * @returns Promise with the API response
 */
export const saveModelProviderConfig = async (
  config: Record<string, unknown>,
): Promise<ApiResponse> => {
  try {
    // Extract API key for header, remove from body
    const { model_api_key, ...bodyConfig } = config;

    // Sanitize API key: trim whitespace and remove non-ISO-8859-1 characters
    // HTTP headers must only contain ISO-8859-1 characters (0x00-0xFF)
    const sanitizedApiKey = ((model_api_key as string) || "")
      .trim()
      .replace(/[^\u0000-\u00FF]/gu, "");

    const response: AxiosResponse<ApiResponse> = await queryEngineClient.put(
      "/v1/model-config",
      bodyConfig,
      {
        headers: {
          "X-Model-API-Key": sanitizedApiKey,
        },
      },
    );
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};
