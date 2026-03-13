import type { AgentSentimentRating } from "@/features/agent-feedback/schema";

import { ThumbsRatingSelector } from "@/features/agent-feedback/components/thumbs-rating-selector";

import { useFieldContext } from "../form-context";

interface ThumbsRatingFieldProps {
  /** Additional className for the container */
  className?: string;
}

/**
 * Pre-bound thumbs up/down rating selector field
 *
 * Wraps `ThumbsRatingSelector` with `useFieldContext` for automatic
 * form field state access. Designed for per-agent binary ratings.
 * Allows deselection (null value).
 *
 * @example
 * ```tsx
 * <form.AppField
 *   name="agentRatings[0].rating"
 *   children={(field) => <field.ThumbsRatingField />}
 * />
 * ```
 */
export function ThumbsRatingField({
  className,
}: ThumbsRatingFieldProps): React.ReactElement {
  const field = useFieldContext<AgentSentimentRating | null>();

  return (
    <ThumbsRatingSelector
      value={field.state.value}
      onChange={field.handleChange}
      className={className}
    />
  );
}
