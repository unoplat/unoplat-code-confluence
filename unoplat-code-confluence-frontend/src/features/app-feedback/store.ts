import { create } from "zustand";

interface AppFeedbackSheetState {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
}

export const useAppFeedbackSheetStore = create<AppFeedbackSheetState>()(
  (set) => ({
    isOpen: false,
    open: () => set({ isOpen: true }),
    close: () => set({ isOpen: false }),
    toggle: () => set((state) => ({ isOpen: !state.isOpen })),
  }),
);
