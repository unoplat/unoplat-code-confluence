import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import type { SentimentRating } from "@/features/agent-feedback/schema";
import {
  getSentimentEmoji,
  getSentimentLabel,
} from "@/features/agent-feedback/utils";
import { cn } from "@/lib/utils";

import { useFieldContext } from "../form-context";

const RATINGS: SentimentRating[] = ["happy", "neutral", "unhappy"];

interface MiniEmojiFieldProps {
  /** Additional className for the container */
  className?: string;
}

/**
 * Pre-bound compact emoji rating selector field
 *
 * Uses `useFieldContext` to access form field state automatically.
 * Designed for per-agent ratings in collapsible sections.
 * Allows deselection (null value) unlike the main EmojiRatingField.
 *
 * @example
 * ```tsx
 * <form.AppField
 *   name="agentRatings[0].rating"
 *   children={(field) => <field.MiniEmojiField />}
 * />
 * ```
 */
export function MiniEmojiField({
  className,
}: MiniEmojiFieldProps): React.ReactElement {
  const field = useFieldContext<SentimentRating | null>();

  return (
    <ToggleGroup
      type="single"
      value={field.state.value ?? ""}
      onValueChange={(newValue) => {
        // Allow deselection by passing null when value is empty
        field.handleChange(newValue ? (newValue as SentimentRating) : null);
      }}
      className={cn("flex items-center gap-1", className)}
    >
      {RATINGS.map((rating) => (
        <ToggleGroupItem
          key={rating}
          value={rating}
          aria-label={getSentimentLabel(rating)}
          size="sm"
          className={cn(
            "h-8 w-8 rounded-lg p-0",
            "data-[state=on]:bg-primary/10 data-[state=on]:ring-1 data-[state=on]:ring-primary",
          )}
        >
          <span className="text-lg" aria-hidden="true">
            {getSentimentEmoji(rating)}
          </span>
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
