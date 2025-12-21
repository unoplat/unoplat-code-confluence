import type { RepositoryAgentCodebaseState } from "@/features/repository-agent-snapshots/transformers";

import type { AgentRatingValue, SentimentRating } from "./schema";
import { AGENT_IDS } from "./schema";

/**
 * Build initial agent ratings array from codebase data
 *
 * Creates a flat array with one entry per codebase-agent combination.
 * Each entry starts with null rating (not rated).
 *
 * @param codebases - Array of codebase states from Electric SQL snapshot
 * @returns Array of agent rating objects initialized with null ratings
 */
export function buildInitialAgentRatings(
  codebases: RepositoryAgentCodebaseState[],
): AgentRatingValue[] {
  return codebases.flatMap((codebase) =>
    AGENT_IDS.map((agentId) => ({
      codebase_name: codebase.codebaseName,
      agent_id: agentId,
      rating: null,
    })),
  );
}

/**
 * Calculate count of "mixed signals" - agents rated differently than overall
 *
 * Mixed signals indicate per-agent ratings that differ from the overall rating.
 * This helps users understand their feedback granularity.
 *
 * @param overallRating - The overall sentiment rating (or undefined if not set)
 * @param agentRatings - Array of per-agent ratings
 * @returns Number of agents with ratings different from overall
 */
export function getMixedSignalsCount(
  overallRating: SentimentRating | undefined,
  agentRatings: AgentRatingValue[],
): number {
  if (!overallRating) return 0;

  return agentRatings.filter(
    (ar) => ar.rating !== null && ar.rating !== overallRating,
  ).length;
}

/**
 * Extract error messages from TanStack Form validation errors
 *
 * TanStack Form returns errors as an array of unknown types.
 * This helper extracts string messages safely.
 *
 * @param errors - Array of error objects from form field meta
 * @returns Array of string error messages
 */
export function getErrorMessages(errors: unknown[]): string[] {
  return errors
    .map((err) => {
      if (typeof err === "string") return err;
      if (typeof err === "object" && err !== null && "message" in err) {
        return (err as { message?: string }).message;
      }
      return undefined;
    })
    .filter((msg): msg is string => Boolean(msg));
}

/**
 * Get emoji icon for sentiment rating
 *
 * @param rating - Sentiment rating value
 * @returns Emoji string for the rating
 */
export function getSentimentEmoji(rating: SentimentRating): string {
  const emojiMap: Record<SentimentRating, string> = {
    happy: "😊",
    neutral: "😐",
    unhappy: "😞",
  };
  return emojiMap[rating];
}

/**
 * Get display label for sentiment rating
 *
 * @param rating - Sentiment rating value
 * @returns Human-readable label for the rating
 */
export function getSentimentLabel(rating: SentimentRating): string {
  const labelMap: Record<SentimentRating, string> = {
    happy: "Happy",
    neutral: "Neutral",
    unhappy: "Unhappy",
  };
  return labelMap[rating];
}
