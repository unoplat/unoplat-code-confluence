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

export interface CodebaseStatus {
  codebaseName: string;
  workflows: WorkflowStatus[];
}

export interface WorkflowStatus {
  workflowId: string;
  workflowRuns: WorkflowRun[];
}

export interface WorkflowRun {
  workflowRunId: string;
  status: string;
  started_at: string;
  currentStage?: string | null;
  completedStages: CompletedStage[];
  totalStages?: number | null;
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
