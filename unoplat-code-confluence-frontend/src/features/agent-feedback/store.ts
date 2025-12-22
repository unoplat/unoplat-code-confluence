import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import {
  AgentRatingValue,
  FeedbackCategory,
  FeedbackStep,
  SentimentRating,
} from "./schema";

/**
 * Draft state for agent feedback form
 * Stores partial form data for persistence across sessions
 */
interface AgentFeedbackDraft {
  overallRating: SentimentRating;
  agentRatings: AgentRatingValue[];
  categories: FeedbackCategory[];
  comments: string;
}

/**
 * Agent feedback store state
 */
interface AgentFeedbackState {
  /** Current form draft data */
  draft: AgentFeedbackDraft;
  /** Current step in the feedback flow */
  step: FeedbackStep;
  /** Update draft with partial data (merges with existing) */
  setDraft: (data: Partial<AgentFeedbackDraft>) => void;
  /** Set current step */
  setStep: (step: FeedbackStep) => void;
  /** Reset store to initial state */
  reset: () => void;
}

/**
 * Initial draft state
 */
const initialDraft: AgentFeedbackDraft = {
  overallRating: SentimentRating.HAPPY,
  agentRatings: [],
  categories: [],
  comments: "",
};

/**
 * Zustand store for agent feedback form state
 *
 * Uses localStorage persistence to preserve draft data across sessions.
 * This protects against accidental sheet close when user has entered data.
 *
 * Usage:
 * - Form reads defaultValues from draft
 * - On step navigation, sync form values to store via setDraft
 * - On successful submission, call reset() to clear draft
 */
export const useAgentFeedbackStore = create<AgentFeedbackState>()(
  persist(
    (set) => ({
      draft: initialDraft,
      step: "rating" as FeedbackStep,

      setDraft: (newData) =>
        set((state) => ({
          draft: { ...state.draft, ...newData },
        })),

      setStep: (step) => set({ step }),

      reset: () =>
        set({
          draft: initialDraft,
          step: "rating" as FeedbackStep,
        }),
    }),
    {
      name: "agent-feedback-draft",
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
