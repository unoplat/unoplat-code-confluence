// New GitHubRepoSummary interface to match the backend model
export interface GitHubRepoSummary {
  name: string;
  owner_url: string;
  private: boolean;
  git_url: string;
  owner_name: string;
}

// Repository metadata type
export interface RepositoryMetadata {
  codebaseFolder: string;
  rootPackage: string;
  programmingLanguage: string;
  packageManager: string;
}

// Repository selection type
export interface RepositorySelection {
  repository: GitHubRepoSummary;
  metadata: RepositoryMetadata;
}

// Ingestion job types
export type IngestionStatus = 'queued' | 'started' | 'in-progress' | 'completed' | 'failed';

export interface IngestionJob {
  id: string;
  repositoryName: string;
  repositoryLink: string;
  status: IngestionStatus;
  createdAt: string;
  updatedAt: string;
  error?: string;
}

export interface PaginationJson {
  page: number;
  perPage: number;
} 


export interface PaginatedResponse<T> {
  items: T[];
  per_page: number;
  has_next: boolean;
  next_cursor?: string;
}


export interface FlagResponse {
  status: boolean;
  errorCode?: number;
}

// Backend-compatible codebase config for repository metadata
export interface ProgrammingLanguageMetadata {
  language: string; // e.g., "python"
  package_manager: string; // e.g., "uv", "pip", "poetry"
  language_version?: string;
}

export interface CodebaseConfig {
  codebase_folder: string;
  root_package?: string;
  programming_language_metadata: ProgrammingLanguageMetadata;
  dependencies?: Array<{
    name: string;
    version: string;
  }>;
}

// Backend-compatible repository configuration request
export interface GitHubRepoRequestConfiguration {
  repository_name: string;
  repository_git_url: string;
  repository_owner_name: string;
  repository_metadata: CodebaseConfig[];
}

// Backend-compatible codebase config for repository metadata (GET response)
export interface CodebaseRepoConfig {
  codebase_folder: string;
  root_package?: string | null;
  programming_language_metadata: ProgrammingLanguageMetadata;
  status?: CodebaseStatusSchema | null;
  dependencies?: Array<{
    name: string;
    version: string;
  }>;
}

export interface GitHubRepoResponseConfiguration {
  repository_name: string;
  repository_owner_name: string;
  repository_workflow_status?: WorkflowStatus | null;
  repository_metadata: CodebaseRepoConfig[];
}

export interface CodebaseStatusSchema {
  codebases: CodebaseStatus[];
}

export interface WorkflowStatus {
  workflowId: string;
  workflowRuns: WorkflowRun[];
}


export interface CompletedStage {
  stageName: string;
  status: string;
}

// Generic API response type for POST/PUT endpoints
export interface ApiResponse {
  success: boolean;
  message?: string;
  error?: string;
}

// Job submission types

// Job status enum for parent workflow and repository status
export type JobStatus = 'SUBMITTED' | 'RUNNING' | 'FAILED' | 'TIMED_OUT' | 'COMPLETED' | 'RETRYING';

// Parent workflow job response from API
export interface ParentWorkflowJobResponse {
  repository_name: string;
  repository_owner_name: string;
  repository_workflow_run_id: string;
  status: JobStatus;
  started_at: string;
  completed_at?: string | null;
}

// Parent workflow jobs list response
export interface ParentWorkflowJobListResponse {
  jobs: ParentWorkflowJobResponse[];
}

// Issue tracking types
export type IssueStatus = 'OPEN' | 'CLOSED';

export interface IssueTracking {
  issue_id?: string | null;
  issue_number?: number | null;
  issue_url?: string | null;
  issue_status?: IssueStatus | null;
  created_at?: string | null;
}

export type IssueType = 'REPOSITORY' | 'CODEBASE';

// ===================================
// ERROR REPORT TYPES
// ===================================

/**
 * Backend-aligned error report type that exactly matches the API schema
 */
export interface ApiErrorReport {
  error_message: string;
  stack_trace?: string | null;
  metadata?: Record<string, unknown> | null;
}

/**
 * Enhanced UI error report that combines API data with UI-specific fields
 */
export interface UiErrorReport extends ApiErrorReport {
  // UI-specific fields
  error_type: IssueType;
  error_traceback?: string; // Alias for stack_trace for backward compatibility
  issue_tracking?: IssueTracking;
  
  // Repository context
  repository_name: string;
  repository_owner_name: string;
  parent_workflow_run_id: string;
  
  // Optional workflow context
  workflow_id?: string;
  workflow_run_id?: string;
  activity_id?: string;
  activity_name?: string;
}

// WorkflowRun model from backend
export interface WorkflowRun {
  codebase_workflow_run_id: string;
  started_at: string;
  status: JobStatus;
  completed_at?: string | null;
  error_report?: ApiErrorReport | null;
  issue_tracking?: IssueTracking | null;
}

// Flattened codebase run for table display
export interface FlattenedCodebaseRun {
  root_package: string,
  codebase_workflow_run_id: string;
  codebase_status: JobStatus;
  codebase_started_at: string;
  codebase_completed_at?: string | null;
  codebase_error_report?: UiErrorReport | null;
  codebase_issue_tracking?: IssueTracking | null;
}

// WorkflowStatus model from backend
export interface WorkflowStatus {
  codebase_workflow_id: string;
  codebase_workflow_runs: WorkflowRun[];
}

// CodebaseStatus model from backend
export interface CodebaseStatus {
  root_package: string;
  workflows: WorkflowStatus[];
}

// CodebaseStatusList model from backend
export interface CodebaseStatusList {
  codebases: CodebaseStatus[];
}

// GithubRepoStatus model from backend
export interface GithubRepoStatus {
  repository_name: string;
  repository_owner_name: string;
  repository_workflow_run_id: string;
  repository_workflow_id: string;
  started_at: string;
  status: JobStatus;
  error_report?: UiErrorReport | null;
  issue_tracking?: IssueTracking | null;
  completed_at?: string | null;
  codebase_status_list?: CodebaseStatusList;
}

// Dictionary mapping programming languages to their supported package managers
export const LANGUAGE_PACKAGE_MANAGERS: Record<string, string[]> = {
  python: ['auto-detect', 'uv', 'pip', 'poetry'],
  // Add more languages as needed
  javascript: ['auto-detect', 'npm', 'yarn', 'pnpm'],
  typescript: ['auto-detect', 'npm', 'yarn', 'pnpm'],
  java: ['auto-detect', 'maven', 'gradle'],
  rust: ['auto-detect', 'cargo']
};
