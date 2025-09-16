import { env } from './env';
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { FlagResponse, GitHubRepoSummary, PaginatedResponse, GitHubRepoRequestConfiguration, GitHubRepoResponseConfiguration, DetectionProgress, DetectionResult, DetectionError, IngestedRepository, IngestedRepositoriesResponse, RefreshRepositoryResponse, CodebaseMetadataResponse } from '../types';
import type { AgentType, ActivityType, SSEEvent, AggregatedSSEEvent, AggregatedAgentsMdEventData } from '@/types/sse';

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

// ===================================
// GENERATE AGENTS.MD - SSE + METADATA
// ===================================

export type ParsedEventInfo = {
  codebase?: string;
  agent?: AgentType;
  activity?: ActivityType | 'status';
};

export interface CodebaseAgentRulesOptions {
  ownerName: string;
  repoName: string;
  codebaseIds: string[];
  agents?: AgentType[];
  activities?: ActivityType[];
  onEvent?: (event: SSEEvent, parsed: ParsedEventInfo) => void;
  onAggregated?: (event: AggregatedSSEEvent) => void;
  onError?: (error: Error) => void;
  signal?: AbortSignal;
}

// Simple counter to tag EventSource connections for debugging
let __sseConnectionCounter = 0;

export const getCodebaseAgentRules = (options: CodebaseAgentRulesOptions): EventSource => {
  const {
    ownerName,
    repoName,
    codebaseIds,
    agents = ['project_configuration_agent', 'development_workflow', 'business_logic_domain'],
    activities = ['prompt.start', 'model.request', 'tool.call', 'tool.result', 'result', 'complete'],
    onEvent,
    onAggregated,
    onError,
    signal,
  } = options;

  const logDebug = (...args: unknown[]): void => {
    // Avoid noisy logs in production unless explicitly enabled
    
      // Prefix for easy filtering in console
      console.log('[SSE]', ...args);
    
  };

  const url = `${env.queryEngineUrl}/v1/codebase-agent-rules?owner_name=${encodeURIComponent(ownerName)}&repo_name=${encodeURIComponent(repoName)}`;
  const connectionId = ++__sseConnectionCounter;
  const ctx = {
    connectionId,
    createdAt: Date.now(),
    onopenCount: 0,
    totalEvents: 0,
    lastEventAt: 0,
    namedEventCounter: {} as Record<string, number>,
    recent: [] as Array<{ name: string; id: string; ts: number }>,
  };
  const markEvent = (name: string, id: string) => {
    ctx.totalEvents += 1;
    ctx.lastEventAt = Date.now();
    ctx.namedEventCounter[name] = (ctx.namedEventCounter[name] || 0) + 1;
    ctx.recent.push({ name, id, ts: Date.now() });
    if (ctx.recent.length > 10) ctx.recent.shift();
  };

  logDebug('Opening EventSource', { connectionId, url, ownerName, repoName, codebaseCount: codebaseIds.length });
  const eventSource = new EventSource(url);
  eventSource.onopen = () => {
    ctx.onopenCount += 1;
    logDebug('EventSource.onopen', {
      connectionId,
      attempt: ctx.onopenCount,
      readyState: eventSource.readyState,
      ts: new Date().toISOString(),
    });
  };

  // Use ownerName/repoName directly as repository qualified name
  const repositoryQualifiedName = `${ownerName}/${repoName}`;
  let aggregatedListenerRegistered = false;

  // Register aggregated listener immediately if onAggregated callback is provided
  if (onAggregated && !aggregatedListenerRegistered) {
    const aggregatedEventName = `${repositoryQualifiedName}:aggregated_final_summary_agent:agent_md_output`;
    logDebug('Registering aggregated listener', { aggregatedEventName });
    eventSource.addEventListener(aggregatedEventName, (aggEvt: MessageEvent) => {
      try {
        const lastId = (aggEvt as unknown as { lastEventId?: string }).lastEventId || '0';
        logDebug('aggregated event received', { event: aggregatedEventName, lastEventId: lastId, length: typeof aggEvt.data === 'string' ? aggEvt.data.length : 0 });
        const parsed = JSON.parse(aggEvt.data) as AggregatedAgentsMdEventData;
        const aggEvent: AggregatedSSEEvent = {
          id: parseInt(lastId),
          event: aggregatedEventName,
          data: parsed,
        };
        markEvent(aggregatedEventName, lastId);
        onAggregated?.(aggEvent);

        // Close the EventSource connection after receiving the final aggregated event
        logDebug('Closing EventSource after aggregated event received');
        eventSource.close();
      } catch (err) {
        onError?.(new Error(`Failed to parse aggregated event ${aggregatedEventName}: ${String(err)}`));
        const snippet = typeof (aggEvt as MessageEvent)?.data === 'string' ? (aggEvt as MessageEvent).data.slice(0, 200) : undefined;
        logDebug('aggregated event parse error', { error: String(err), snippet });
      }
    });
    aggregatedListenerRegistered = true;
  }

  eventSource.addEventListener('status', (event: MessageEvent) => {
    try {
      const lastEventId = (event as unknown as { lastEventId?: string }).lastEventId || '0';
      logDebug('status event received', { lastEventId, length: typeof event.data === 'string' ? event.data.length : 0 });
      const sseEvent: SSEEvent = {
        id: parseInt(lastEventId),
        event: 'status',
        data: JSON.parse(event.data),
      } as SSEEvent;
      markEvent('status', lastEventId);
      onEvent?.(sseEvent, { activity: 'status' });
    } catch (err) {
      onError?.(new Error(`Failed to parse status event: ${String(err)}`));
      const snippet = typeof (event as MessageEvent)?.data === 'string' ? (event as MessageEvent).data.slice(0, 200) : undefined;
      logDebug('status event parse error', { error: String(err), snippet });
    }
  });

  codebaseIds.forEach((codebase) => {
    agents.forEach((agent) => {
      activities.forEach((activity) => {
        const eventName = `${codebase}:${agent}:${activity}`;
        logDebug('Registering listener', { eventName });
        eventSource.addEventListener(eventName, (event: MessageEvent) => {
          try {
            const lastEventId = (event as unknown as { lastEventId?: string }).lastEventId || '0';
            logDebug('named event received', { event: eventName, lastEventId, length: typeof event.data === 'string' ? event.data.length : 0 });
            const sseEvent: SSEEvent = {
              id: parseInt(lastEventId),
              event: eventName,
              data: JSON.parse(event.data),
            } as SSEEvent;
            markEvent(eventName, lastEventId);
            onEvent?.(sseEvent, { codebase, agent, activity });
          } catch (err) {
            onError?.(new Error(`Failed to parse event ${eventName}: ${String(err)}`));
            const snippet = typeof (event as MessageEvent)?.data === 'string' ? (event as MessageEvent).data.slice(0, 200) : undefined;
            logDebug('named event parse error', { event: eventName, error: String(err), snippet });
          }
        });
      });
    });
  });

  eventSource.onerror = () => {
    // Allow EventSource to auto-reconnect; don't close here.
    const now = Date.now();
    const msSinceLast = ctx.lastEventAt ? now - ctx.lastEventAt : null;
    const uptimeMs = now - ctx.createdAt;
    const last = ctx.recent[ctx.recent.length - 1];
    const lastWasComplete = last?.name?.endsWith(':complete') ?? false;
    // Build a compact per-type summary, avoid flooding the console
    const byTypeSummary = Object.entries(ctx.namedEventCounter)
      .slice(0, 20)
      .reduce((acc, [k, v]) => ({ ...acc, [k]: v }), {} as Record<string, number>);

    logDebug('EventSource.onerror', {
      connectionId: ctx.connectionId,
      attempt: ctx.onopenCount,
      readyState: eventSource.readyState,
      uptimeMs,
      msSinceLastEvent: msSinceLast,
      totalEvents: ctx.totalEvents,
      lastEventName: last?.name,
      lastEventId: last?.id,
      lastWasComplete,
      recentEvents: ctx.recent.slice(-5),
      byTypeSummary,
      ts: new Date(now).toISOString(),
    });
    onError?.(new Error('SSE connection failed'));
  };

  if (signal) {
    signal.addEventListener('abort', () => {
      logDebug('Abort signal received, closing EventSource');
      eventSource.close();
    });
  }

  return eventSource;
};

export async function getCodebaseMetadata(
  repositoryOwnerName: string,
  repositoryName: string
): Promise<CodebaseMetadataResponse> {
  try {
    const params = {
      repository_owner_name: repositoryOwnerName,
      repository_name: repositoryName,
    } as Record<string, string>;
    const res: AxiosResponse<CodebaseMetadataResponse> = await apiClient.get('/codebase-metadata', { params });
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
