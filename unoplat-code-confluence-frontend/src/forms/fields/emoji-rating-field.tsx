import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import type { SentimentRating } from "@/features/agent-feedback/schema";
import {
  getSentimentEmoji,
  getSentimentLabel,
} from "@/features/agent-feedback/utils";
import { cn } from "@/lib/utils";

import { useFieldContext } from "../form-context";
import { getFieldErrorMessages } from "../utils";

const RATINGS: SentimentRating[] = ["happy", "neutral", "unhappy"];

interface EmojiRatingFieldProps {
  /** Additional className for the container */
  className?: string;
}

/**
 * Pre-bound large emoji rating selector field
 *
 * Uses `useFieldContext` to access form field state automatically.
 * Designed for overall rating selection with prominent emoji display.
 *
 * @example
 * ```tsx
 * <form.AppField
 *   name="overallRating"
 *   children={(field) => <field.EmojiRatingField />}
 * />
 * ```
 */
export function EmojiRatingField({
  className,
}: EmojiRatingFieldProps): React.ReactElement {
  const field = useFieldContext<SentimentRating | undefined>();
  const errors = getFieldErrorMessages(field.state.meta.errors);

  return (
    <div className="space-y-3">
      <ToggleGroup
        type="single"
        variant="card"
        size="card"
        value={field.state.value ?? ""}
        onValueChange={(newValue) => {
          if (newValue) {
            field.handleChange(newValue as SentimentRating);
          }
        }}
        className={cn("w-full gap-2.5", className)}
      >
        {RATINGS.map((rating) => (
          <ToggleGroupItem
            key={rating}
            value={rating}
            aria-label={getSentimentLabel(rating)}
          >
            <span className="text-2xl leading-7" aria-hidden="true">
              {getSentimentEmoji(rating)}
            </span>
            <span className="text-xs leading-4 font-medium">
              {getSentimentLabel(rating)}
            </span>
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
      {errors.length > 0 && (
        <p className="text-destructive text-center text-sm">{errors[0]}</p>
      )}
    </div>
  );
}
