export interface Repository {
  id: number;
  name: string;
  full_name: string;
  html_url: string;
  description: string | null;
  private: boolean;
  owner: {
    login: string;
    avatar_url: string;
  };
  updated_at: string;
}

export type RepositoryCategory = 'personal' | 'organization' | 'collaborator';

export interface RepositoryWithCategory extends Repository {
  category: RepositoryCategory;
}

export interface RepositoryMetadata {
  codebaseFolder: string;
  rootPackages: string[];
  programmingLanguage: string;
  packageManager: string;
}

export interface RepositorySelection {
  repository: Repository;
  metadata: RepositoryMetadata;
}

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

 