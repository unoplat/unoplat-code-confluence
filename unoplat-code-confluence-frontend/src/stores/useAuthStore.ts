// stores/useAuthStore.ts
import { create } from "zustand";
import type { GitHubUser } from "@/lib/api";

interface AuthState {
  user: GitHubUser | null;
  setUser: (u: GitHubUser | null) => void;
  reset: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  reset: () => set({ user: null }),
}));
