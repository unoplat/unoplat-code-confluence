import { z } from "zod";

import {
  SentimentRating,
  sentimentRatingSchema,
} from "@/features/agent-feedback/schema";

/**
 * App feedback category enum
 * Matches backend AppFeedbackCategory enum
 */
export const AppFeedbackCategory = {
  BUG_REPORT: "bug_report",
  FEATURE_REQUEST: "feature_request",
  GENERAL: "general",
} as const;

export type AppFeedbackCategory =
  (typeof AppFeedbackCategory)[keyof typeof AppFeedbackCategory];

/**
 * Display labels for app feedback categories
 */
export const CATEGORY_LABELS: Record<AppFeedbackCategory, string> = {
  [AppFeedbackCategory.BUG_REPORT]: "Bug Report",
  [AppFeedbackCategory.FEATURE_REQUEST]: "Feature Request",
  [AppFeedbackCategory.GENERAL]: "General",
};

/**
 * Zod schema for app feedback category validation
 */
export const appFeedbackCategorySchema = z.enum([
  AppFeedbackCategory.BUG_REPORT,
  AppFeedbackCategory.FEATURE_REQUEST,
  AppFeedbackCategory.GENERAL,
]);

/**
 * Full form schema for app feedback
 */
export const appFeedbackSchema = z.object({
  category: appFeedbackCategorySchema,
  sentiment: sentimentRatingSchema,
  subject: z
    .string()
    .min(3, "Subject must be at least 3 characters")
    .max(100, "Subject must be 100 characters or less"),
  description: z
    .string()
    .min(10, "Description must be at least 10 characters")
    .max(2000, "Description must be 2000 characters or less"),
});

export type AppFeedbackFormValues = z.infer<typeof appFeedbackSchema>;

// Re-export SentimentRating for convenience within this feature
export type { SentimentRating };
