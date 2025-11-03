import { create } from 'zustand';
import { type RepositoryConfig } from '../../components/custom/CodebaseForm';

interface RepositoryConfigState {
  // Map of repository name to repository config
  repositoryConfigs: Record<string, RepositoryConfig>;
  selectedRepository: string | null;
  saveStatus: {
    repoName: string | null;
    success: boolean;
    hasCodebases: boolean;
  } | null;
}

interface RepositoryConfigActions {
  setRepositoryConfigs: (configs: Record<string, RepositoryConfig>) => void;
  addRepositoryConfig: (config: RepositoryConfig) => void;
  setSelectedRepository: (repoName: string | null) => void;
  setSaveStatus: (status: RepositoryConfigState['saveStatus']) => void;
  clearSaveStatus: () => void;
}

/**
 * Store for managing repository configurations and selection state
 */
export const useRepositoryConfigStore = create<RepositoryConfigState & RepositoryConfigActions>()((set) => ({
  // Initial state
  repositoryConfigs: {},
  selectedRepository: null,
  saveStatus: null,

  // Actions
  setRepositoryConfigs: (configs) => {
    console.log('[RepositoryConfigStore] Setting multiple configs:', Object.keys(configs));
    set({ repositoryConfigs: configs });
  },
  
  addRepositoryConfig: (config) => {
    console.log('[RepositoryConfigStore] Adding/updating repository config:', config.repositoryName);
    console.log('[RepositoryConfigStore] Codebases count:', config.codebases?.length || 0);
    
    const hasCodebases = !!config.codebases && config.codebases.length > 0;
    console.log('[RepositoryConfigStore] Has codebases:', hasCodebases);
    
    set((state) => {
      const newState = {
        repositoryConfigs: {
          ...state.repositoryConfigs,
          [config.repositoryName]: config
        },
        saveStatus: {
          repoName: config.repositoryName,
          success: true,
          hasCodebases: hasCodebases
        }
      };
      
      console.log('[RepositoryConfigStore] New state after adding config:', {
        configsCount: Object.keys(newState.repositoryConfigs).length,
        saveStatus: newState.saveStatus
      });
      
      return newState;
    });
  },
  
  setSelectedRepository: (repoName) => {
    console.log('[RepositoryConfigStore] Setting selected repository:', repoName);
    set({ selectedRepository: repoName });
  },
  
  setSaveStatus: (status) => {
    console.log('[RepositoryConfigStore] Setting save status:', status);
    set({ saveStatus: status });
  },
  
  clearSaveStatus: () => {
    console.log('[RepositoryConfigStore] Clearing save status');
    set({ saveStatus: null });
  }
})); 