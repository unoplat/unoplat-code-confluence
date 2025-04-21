// stores/useAuthStore.ts
import { create } from 'zustand';
import type { FlagResponse } from '@/types';
import type { GitHubUser } from '@/lib/api';

interface AuthState {
  tokenStatus: FlagResponse | null;
  user: GitHubUser | null;
  setTokenStatus: (t: FlagResponse | null) => void;
  setUser: (u: GitHubUser | null) => void;
  reset: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  tokenStatus: null,
  user:        null,
  setTokenStatus: (tokenStatus) => set({ tokenStatus }),
  setUser:        (user)        => set({ user }),
  reset: () => set({ tokenStatus: null, user: null }),
}));