import { env } from './env';
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { FlagResponse, GitHubRepoSummary, PaginatedResponse, GitHubRepoRequestConfiguration, GitHubRepoResponseConfiguration, DetectionProgress, DetectionResult, DetectionError, IngestedRepository, IngestedRepositoriesResponse, RefreshRepositoryResponse } from '../types';

// Re-export types from '../types' for consumers
export type { FlagResponse, GitHubRepoSummary, PaginatedResponse, DetectionProgress, DetectionResult, DetectionError, IngestedRepository, IngestedRepositoriesResponse, RefreshRepositoryResponse };

/**
 * API Services
 * 
 * Collection of API service functions for backend communication.
 */

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 10000, // 10 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

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
  console.error('API Error:', error);
  
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiResponse>;
    return {
      message: axiosError.response?.data?.message || axiosError.message || 'Unknown API error',
      statusCode: axiosError.response?.status,
      details: axiosError.response?.data,
      isAxiosError: true
    };
  }
  
  return {
    message: error instanceof Error ? error.message : 'Unknown error',
    isAxiosError: false,
    details: error
  };
};

/**
 * Submit GitHub PAT token to the backend
 * 
 * @param token - GitHub Personal Access Token
 * @returns Promise with the response data
 */
export const submitGitHubToken = async (token: string): Promise<ApiResponse> => {
  try {
    // Pass null as data and override Content-Type header
    const response: AxiosResponse<ApiResponse> = await apiClient.post('/ingest-token', null, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': undefined, // Prevent sending default Content-Type
      },
    });

    return response.data;
  } catch (error: unknown) {
    const apiError = handleApiError(error);
    
    // If we have a valid response from the server, return it
    // This might occur for non-2xx status codes that still carry a meaningful API response body
    if (apiError.isAxiosError && apiError.statusCode && apiError.details && typeof apiError.details === 'object' && apiError.details !== null && 'success' in apiError.details) {
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
 * @param search - Optional search term
 * @param cursor - Optional cursor for pagination
 * @returns Promise with paginated GitHub repositories
 */
export const fetchGitHubRepositories = async (
  page: number, 
  perPage: number, 
  filterValues?: Record<string, string | string[] | null>, 
  cursor?: string
): Promise<PaginatedResponse<GitHubRepoSummary>> => {
  try {
    const params: Record<string, string | number> = { page, per_page: perPage };
    
    if (filterValues) {
      params.filterValues = JSON.stringify(filterValues);
    }
    
    if (cursor) {
      params.cursor = cursor;
    }
    
    const response: AxiosResponse<PaginatedResponse<GitHubRepoSummary>> = await apiClient.get('/repos', { params });
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
export const submitRepositoryConfig = async (repositoryConfig: GitHubRepoRequestConfiguration): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.post('/start-ingestion', repositoryConfig);
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

/**
 * Delete GitHub PAT token from the backend
 * 
 * @returns Promise with the response data
 */
/**
 * Update GitHub PAT token in the backend
 * 
 * @param token - GitHub Personal Access Token
 * @returns Promise with the response data
 */
export const updateGitHubToken = async (token: string): Promise<ApiResponse> => {
  try {
    // Pass null as data and override Content-Type header
    const response: AxiosResponse<ApiResponse> = await apiClient.put('/update-token', null, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': undefined, // Prevent sending default Content-Type
      },
    });

    return response.data;
  } catch (error: unknown) {
    const apiError = handleApiError(error);
    
    // If we have a valid response from the server, return it
    // This might occur for non-2xx status codes that still carry a meaningful API response body
    if (apiError.isAxiosError && apiError.statusCode && apiError.details && typeof apiError.details === 'object' && apiError.details !== null && 'success' in apiError.details) {
      // Attempt to cast details to ApiResponse if it looks like one
      return apiError.details as ApiResponse;
    }
    
    // Otherwise, throw the standardized error object for further handling upstream
    throw apiError;
  }
};

export const deleteGitHubToken = async (): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.delete('/delete-token');
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};


export const getFlagStatus = async (flagName: string): Promise<FlagResponse> => {
  try {
    const response: AxiosResponse<FlagResponse> = await apiClient.get(`/flags/${flagName}`);
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
  config: GitHubRepoRequestConfiguration
): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.post('/repository-data', config);
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
  ownerName: string
): Promise<GitHubRepoResponseConfiguration | null> => {
  try {
    const response: AxiosResponse<GitHubRepoResponseConfiguration> = await apiClient.get('/repository-data', {
      params: { repository_name: repositoryName, repository_owner_name: ownerName },
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
 */
export async function fetchGitHubUser(): Promise<GitHubUser> {
  // Get the token from backend
  const response: AxiosResponse<GitHubUser> = await apiClient.get('/user-details');
  return response.data;
}

/**
 * Fetch all parent workflow jobs
 * 
 * @returns Promise with the parent workflow jobs list response
 */
export const getParentWorkflowJobs = async (): Promise<import('../types').ParentWorkflowJobListResponse> => {
  console.log('[API] getParentWorkflowJobs called');
  try {
    const response: AxiosResponse<import('../types').ParentWorkflowJobListResponse> = await apiClient.get('/parent-workflow-jobs');
    console.log('[API] getParentWorkflowJobs response data:', response.data);
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
  workflowRunId: string
): Promise<import('../types').GithubRepoStatus> => {
  console.log('[API] getRepositoryStatus called with params:', { repositoryName, repositoryOwnerName, workflowRunId });
  try {
    const params = {
      repository_name: repositoryName,
      repository_owner_name: repositoryOwnerName,
      workflow_run_id: workflowRunId
    };
    console.log('[API] getRepositoryStatus params:', params);
    const response: AxiosResponse<import('../types').GithubRepoStatus> = await apiClient.get('/repository-status', { params });
    console.log('[API] getRepositoryStatus response data:', response.data);
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
  requestData: GithubIssueSubmissionRequest
): Promise<IssueTracking> => {
  console.log('[API] submitFeedback request data:', requestData);
  try {
    const response: AxiosResponse<IssueTracking> = await apiClient.post('/code-confluence/issues', requestData);
    console.log('[API] submitFeedback response data:', response.data);
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

/**
 * Options for detecting codebases with SSE
 */
export interface DetectCodebasesOptions {
  gitUrl: string;
  isLocal?: boolean;
  onProgress?: (progress: DetectionProgress) => void;
  onResult?: (result: DetectionResult) => void;
  onError?: (error: DetectionError) => void;
  signal?: AbortSignal;
}

/**
 * Detect codebases using Server-Sent Events
 * 
 * @param options - Detection options including gitUrl and event handlers
 * @returns Promise with the detection result
 */
export const detectCodebasesSSE = async (options: DetectCodebasesOptions): Promise<DetectionResult> => {
  const { gitUrl, isLocal = false, onProgress, onResult, onError, signal } = options;
  
  return new Promise((resolve, reject) => {
    // Build the URL with query parameters
    const url = `${env.apiBaseUrl}/detect-codebases-sse?git_url=${encodeURIComponent(gitUrl)}&is_local=${isLocal}`;
    
    // Create EventSource for SSE connection
    const eventSource = new EventSource(url);
    let hasCompleted = false;
    
    // Handle abort signal
    if (signal) {
      signal.addEventListener('abort', () => {
        eventSource.close();
        if (!hasCompleted) {
          reject(new Error('Detection aborted'));
        }
      });
    }
    
    // Connected event handler
    eventSource.addEventListener('connected', () => {
      console.log('[SSE] Connected to detection stream');
    });
    
    // Progress event handler
    eventSource.addEventListener('progress', (event: MessageEvent) => {
      try {
        const progress: DetectionProgress = JSON.parse(event.data);
        console.log('[SSE] Progress:', progress);
        onProgress?.(progress);
      } catch (error) {
        console.error('[SSE] Failed to parse progress event:', error);
      }
    });
    
    // Result event handler
    eventSource.addEventListener('result', (event: MessageEvent) => {
      try {
        const result: DetectionResult = JSON.parse(event.data);
        console.log('[SSE] Result:', result);
        hasCompleted = true;
        onResult?.(result);
        resolve(result);
      } catch (error) {
        console.error('[SSE] Failed to parse result event:', error);
        reject(new Error('Failed to parse detection result'));
      }
    });
    
    // Error event handler
    eventSource.addEventListener('error', (event: MessageEvent) => {
      try {
        if (event.data) {
          const error: DetectionError = JSON.parse(event.data);
          console.error('[SSE] Detection error:', error);
          hasCompleted = true;
          onError?.(error);
          reject(new Error(error.error));
        }
      } catch (parseError) {
        console.error('[SSE] Failed to parse error event:', parseError);
      }
    });
    
    // Done event handler
    eventSource.addEventListener('done', () => {
      console.log('[SSE] Detection stream complete');
      eventSource.close();
    });
    
    // Generic error handler for connection issues
    eventSource.onerror = (error) => {
      console.error('[SSE] Connection error:', error);
      eventSource.close();
      
      if (!hasCompleted) {
        const detectionError: DetectionError = {
          error: 'Connection to detection service failed',
          timestamp: new Date().toISOString(),
          type: 'CONNECTION_ERROR'
        };
        onError?.(detectionError);
        reject(new Error(detectionError.error));
      }
    };
  });
};

/**
 * Fetch ingested repositories from the backend
 * 
 * @returns Promise with ingested repositories data
 */
export const getIngestedRepositories = async (): Promise<IngestedRepositoriesResponse> => {
  try {
    const response: AxiosResponse<IngestedRepositoriesResponse> = await apiClient.get('/get/ingestedRepositories');
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
export const refreshRepository = async (repository: IngestedRepository): Promise<RefreshRepositoryResponse> => {
  try {
    const response: AxiosResponse<RefreshRepositoryResponse> = await apiClient.post('/refresh-repository', repository);
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
export const deleteRepository = async (repository: import('../types').IngestedRepository): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.delete('/delete-repository', { data: repository });
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};