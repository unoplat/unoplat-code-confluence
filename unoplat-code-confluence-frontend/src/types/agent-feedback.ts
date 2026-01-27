/**
 * Types for Agent MD Feedback feature
 * Supports overall repository rating and per-agent per-codebase ratings
 */

import type { AgentTypeValue } from "@/lib/agent-events-utils";

/**
 * Sentiment rating options matching the emoji selector UI
 */
export type SentimentRating = "happy" | "neutral" | "unhappy";

/**
 * Feedback improvement categories
 */
export type FeedbackCategory = "accuracy" | "missing" | "other";

/**
 * Individual agent rating within a specific codebase
 */
export interface AgentRating {
  codebaseName: string;
  agentId: AgentTypeValue;
  rating: SentimentRating | null;
}

/**
 * Complete feedback form data structure
 */
export interface AgentFeedbackFormData {
  /** Required overall repository rating */
  overallRating: SentimentRating;
  /** Optional per-agent per-codebase ratings */
  agentRatings: AgentRating[];
  /** Selected improvement categories */
  categories: FeedbackCategory[];
  /** Free-text comments (markdown supported) */
  comments: string;
}

/**
 * Feedback step in the multi-step flow
 */
export type FeedbackStep = "rating" | "details" | "success";

/**
 * Display configuration for each sentiment rating
 */
export interface SentimentConfig {
  emoji: string;
  label: string;
  colorClass: string;
  bgClass: string;
}

/**
 * Registry of sentiment rating display configurations
 */
export const SENTIMENT_CONFIG: Record<SentimentRating, SentimentConfig> = {
  happy: {
    emoji: "😊",
    label: "Happy",
    colorClass: "text-green-500",
    bgClass: "bg-green-500/10",
  },
  neutral: {
    emoji: "😐",
    label: "Neutral",
    colorClass: "text-amber-500",
    bgClass: "bg-amber-500/10",
  },
  unhappy: {
    emoji: "😞",
    label: "Unhappy",
    colorClass: "text-red-500",
    bgClass: "bg-red-500/10",
  },
};

/**
 * Display configuration for feedback categories
 */
export interface CategoryConfig {
  label: string;
  description: string;
}

/**
 * Registry of feedback category display configurations
 */
export const CATEGORY_CONFIG: Record<FeedbackCategory, CategoryConfig> = {
  accuracy: {
    label: "Accuracy issues",
    description: "Generated content contains incorrect information",
  },
  missing: {
    label: "Missing information",
    description: "Important details were not captured",
  },
  other: {
    label: "Other",
    description: "Other feedback or suggestions",
  },
};

/**
 * Initial form state factory
 */
export function createInitialFeedbackData(): AgentFeedbackFormData {
  return {
    overallRating: "happy",
    agentRatings: [],
    categories: [],
    comments: "",
  };
}

/**
 * Check if any agent ratings differ from the overall rating
 * Used to show "mixed signals" summary in the details screen
 */
export function getMixedSignalAgents(
  formData: AgentFeedbackFormData,
): AgentRating[] {
  return formData.agentRatings.filter(
    (ar) => ar.rating !== null && ar.rating !== formData.overallRating,
  );
}

/**
 * Format feedback data as markdown for GitHub issue body
 */
export function formatFeedbackAsMarkdown(
  formData: AgentFeedbackFormData,
  repositoryName: string,
  runId: string,
): string {
  const lines: string[] = [];

  lines.push("## Agent MD Feedback");
  lines.push("");
  lines.push(`**Repository:** ${repositoryName}`);
  lines.push(`**Run ID:** \`${runId}\``);
  lines.push("");

  // Overall rating
  const overallConfig = SENTIMENT_CONFIG[formData.overallRating];
  lines.push(
    `### Overall Rating: ${overallConfig.emoji} ${overallConfig.label}`,
  );
  lines.push("");

  // Categories
  if (formData.categories.length > 0) {
    lines.push("### Categories");
    for (const category of formData.categories) {
      const config = CATEGORY_CONFIG[category];
      lines.push(`- ${config.label}`);
    }
    lines.push("");
  }

  // Per-agent ratings (if any differ from overall)
  const mixedSignals = getMixedSignalAgents(formData);
  if (mixedSignals.length > 0) {
    lines.push("### Individual Agent Ratings");
    lines.push("");
    lines.push("| Codebase | Agent | Rating |");
    lines.push("|----------|-------|--------|");
    for (const agentRating of mixedSignals) {
      const config = SENTIMENT_CONFIG[agentRating.rating!];
      lines.push(
        `| ${agentRating.codebaseName} | ${agentRating.agentId} | ${config.emoji} ${config.label} |`,
      );
    }
    lines.push("");
  }

  // Comments
  if (formData.comments.trim()) {
    lines.push("### Comments");
    lines.push("");
    lines.push(formData.comments);
    lines.push("");
  }

  lines.push("---");
  lines.push("*Submitted via Agent MD Feedback*");

  return lines.join("\n");
}
