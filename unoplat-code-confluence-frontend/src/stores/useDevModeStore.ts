import { create } from "zustand"
import { persist, createJSONStorage } from "zustand/middleware"

interface DevModeState {
  isDevMode: boolean
  setDevMode: (value: boolean) => void
}

export const useDevModeStore = create<DevModeState>()(
  persist(
    (set) => ({
      isDevMode: false,
      setDevMode: (value: boolean) => set({ isDevMode: value }),
    }),
    {
      name: "dev-mode-storage",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ isDevMode: state.isDevMode }),
    }
  )
) 