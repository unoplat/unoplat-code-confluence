import { z } from "zod";

/**
 * Sentiment rating enum for feedback
 * Matches backend SentimentRating enum in routers/github_issues/models.py
 */
export const SentimentRating = {
  HAPPY: "happy",
  NEUTRAL: "neutral",
  UNHAPPY: "unhappy",
} as const;

export type SentimentRating =
  (typeof SentimentRating)[keyof typeof SentimentRating];

/**
 * Feedback category enum for categorizing feedback
 * Matches backend FeedbackCategory enum in routers/github_issues/models.py
 */
export const FeedbackCategory = {
  ACCURACY: "accuracy",
  MISSING: "missing",
  OTHER: "other",
} as const;

export type FeedbackCategory =
  (typeof FeedbackCategory)[keyof typeof FeedbackCategory];

/**
 * Display labels for feedback categories
 */
export const FEEDBACK_CATEGORY_LABELS: Record<FeedbackCategory, string> = {
  [FeedbackCategory.ACCURACY]: "Accuracy issues",
  [FeedbackCategory.MISSING]: "Missing information",
  [FeedbackCategory.OTHER]: "Other",
};

/**
 * Agent IDs for per-agent ratings
 * These correspond to the three agents generated in the AGENTS.md workflow
 */
export const AGENT_IDS = [
  "project-configuration",
  "development-workflow",
  "business-logic",
] as const;

export type AgentId = (typeof AGENT_IDS)[number];

/**
 * Display labels for agent IDs
 */
export const AGENT_ID_LABELS: Record<AgentId, string> = {
  "project-configuration": "Project Configuration",
  "development-workflow": "Development Workflow",
  "business-logic": "Business Logic",
};

/**
 * Feedback step for navigation
 */
export const FeedbackStep = {
  RATING: "rating",
  DETAILS: "details",
  SUCCESS: "success",
} as const;

export type FeedbackStep = (typeof FeedbackStep)[keyof typeof FeedbackStep];

// ─────────────────────────────────────────────────
// Zod Schemas
// ─────────────────────────────────────────────────

/**
 * Schema for sentiment rating validation
 */
export const sentimentRatingSchema = z.enum([
  SentimentRating.HAPPY,
  SentimentRating.NEUTRAL,
  SentimentRating.UNHAPPY,
]);

/**
 * Schema for feedback category validation
 */
export const feedbackCategorySchema = z.enum([
  FeedbackCategory.ACCURACY,
  FeedbackCategory.MISSING,
  FeedbackCategory.OTHER,
]);

/**
 * Schema for overall rating field with custom error message
 */
export const overallRatingSchema = sentimentRatingSchema.refine(
  (val) => val !== undefined,
  { message: "Please select an overall rating" },
);

/**
 * Schema for comments field with length validation
 */
export const commentsSchema = z
  .string()
  .max(1000, "Comments must be 1000 characters or less")
  .optional();

/**
 * Schema for categories array
 */
export const categoriesSchema = z.array(feedbackCategorySchema);

/**
 * Schema for per-agent rating
 */
export const agentRatingSchema = z.object({
  codebase_name: z.string(),
  agent_id: z.string(),
  rating: sentimentRatingSchema.nullable(),
});

export type AgentRatingValue = z.infer<typeof agentRatingSchema>;

/**
 * Full form schema for agent feedback
 */
export const agentFeedbackSchema = z.object({
  overallRating: sentimentRatingSchema,
  agentRatings: z.array(agentRatingSchema),
  categories: categoriesSchema,
  comments: commentsSchema,
});

export type AgentFeedbackFormValues = z.infer<typeof agentFeedbackSchema>;
