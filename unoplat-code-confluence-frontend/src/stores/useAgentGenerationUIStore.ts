import { create } from 'zustand';
import type { IngestedRepository } from '@/types';

interface AgentGenerationUIState {
  activeTab: string | null;
  isDialogOpen: boolean;
  isPreviewOpen: boolean;
  selectedRepository: IngestedRepository | null;

  setActiveTab: (tab: string | null) => void;
  openDialog: (repository: IngestedRepository) => void;
  closeDialog: () => void;
  openPreview: () => void;
  closePreview: () => void;
}

export const useAgentGenerationUIStore = create<AgentGenerationUIState>()((set) => ({
  activeTab: null,
  isDialogOpen: false,
  isPreviewOpen: false,
  selectedRepository: null,

  setActiveTab: (tab) => set({ activeTab: tab }),
  openDialog: (repository) => set({ isDialogOpen: true, selectedRepository: repository, activeTab: null }),
  closeDialog: () => set({ isDialogOpen: false, selectedRepository: null, activeTab: null }),
  openPreview: () => set({ isPreviewOpen: true }),
  closePreview: () => set({ isPreviewOpen: false }),
}));


