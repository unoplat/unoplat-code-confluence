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
