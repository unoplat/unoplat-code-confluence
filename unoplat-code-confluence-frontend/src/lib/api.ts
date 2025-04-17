import { env } from './env';
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { FlagResponse, GitHubRepoSummary, PaginatedResponse, GitHubRepoRequestConfiguration, GitHubRepoResponseConfiguration } from '../types';

// Re-export types from '../types' for consumers
export type { FlagResponse, GitHubRepoSummary, PaginatedResponse };

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
 * Update repository data (configuration) in the backend
 * @param config - Repository configuration payload
 * @returns Promise with the response data
 */
export const updateRepositoryData = async (
  config: GitHubRepoRequestConfiguration
): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.put('/repository-data', config);
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

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