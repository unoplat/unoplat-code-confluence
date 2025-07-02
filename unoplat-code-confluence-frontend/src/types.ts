// New GitHubRepoSummary interface to match the backend model
export interface GitHubRepoSummary {
  name: string;
  owner_url: string;
  private: boolean;
  git_url: string;
  owner_name: string;
}

// Local repository data interface
export interface LocalRepositoryData {
  repositoryPath: string;
  repositoryName: string;
  repositorySource: "local";
}

// Repository configuration for dialog props - supports both GitHub and local repositories
export interface RepositoryConfigDialogData {
  repositoryName: string;
  repositoryGitUrl: string;
  repositoryOwnerName: string;
  isLocal?: boolean;
  localPath?: string;
}

// Repository metadata type
export interface RepositoryMetadata {
  codebaseFolder: string;
  rootPackages: string[];
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
  language_version?: string | null;
  role?: 'leaf' | 'aggregator' | 'NA';
  manifest_path?: string | null;
  project_name?: string | null;
}

export interface CodebaseConfig {
  codebase_folder: string;
  root_packages?: string[] | null;
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
  is_local: boolean; // Whether it's a local repository
  local_path?: string | null; // Local path for local repositories
}

// Backend-compatible codebase config for repository metadata (GET response)
export interface CodebaseRepoConfig {
  codebase_folder: string;
  root_packages?: string[] | null;
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
  codebase_folder: string,
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
  codebase_folder: string;
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
  python: ['uv', 'pip', 'poetry'],
  // Add more languages as needed
  javascript: ['npm', 'yarn', 'pnpm'],
  typescript: ['npm', 'yarn', 'pnpm'],
  java: ['maven', 'gradle'],
  rust: ['cargo'],
};

// ===================================
// CODEBASE DETECTION TYPES
// ===================================

export interface DetectionProgress {
  state: 'initializing' | 'cloning' | 'analyzing' | 'complete';
  message: string;
  repository_url: string;
}

export interface DetectionResult {
  repository_url: string;
  duration_seconds: number;
  codebases: CodebaseConfig[];
  error: string | null;
}

export interface DetectionError {
  error: string;
  timestamp: string;
  type: 'DETECTION_ERROR' | 'CONNECTION_ERROR' | 'AUTH_ERROR';
}

export interface SSEEvent<T = unknown> {
  event: string;
  data: T;
}

// ===================================
// INGESTED REPOSITORY TYPES  
// ===================================

export interface IngestedRepository {
  repository_name: string;
  repository_owner_name: string;
  is_local: boolean;
  local_path?: string | null;
}

export interface IngestedRepositoriesResponse {
  repositories: IngestedRepository[];
}

// Refresh repository response from the backend
export interface RefreshRepositoryResponse {
  repository_name: string;
  repository_owner_name: string;
  workflow_id: string;
  run_id: string;
}
