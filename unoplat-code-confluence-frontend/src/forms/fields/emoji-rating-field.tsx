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
        value={field.state.value ?? ""}
        onValueChange={(newValue) => {
          // Only trigger onChange if a value is selected (prevent deselection)
          if (newValue) {
            field.handleChange(newValue as SentimentRating);
          }
        }}
        className={cn(
          "mx-auto flex w-full max-w-md items-center justify-between gap-4 py-4",
          className,
        )}
      >
        {RATINGS.map((rating) => (
          <ToggleGroupItem
            key={rating}
            value={rating}
            aria-label={getSentimentLabel(rating)}
            className={cn(
              "flex h-auto min-w-[100px] flex-1 flex-col items-center gap-3 rounded-xl border border-transparent px-4 py-6",
              "hover:bg-muted/50",
              "data-[state=on]:border-primary/30 data-[state=on]:bg-primary/10 data-[state=on]:ring-primary data-[state=on]:ring-2",
            )}
          >
            <span className="text-5xl" aria-hidden="true">
              {getSentimentEmoji(rating)}
            </span>
            <span className="text-sm font-medium">
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
