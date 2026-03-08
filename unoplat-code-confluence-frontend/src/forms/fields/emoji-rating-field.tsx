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
          if (newValue) {
            field.handleChange(newValue as SentimentRating);
          }
        }}
        className={cn(
          "flex w-full items-center justify-center gap-[10px]",
          className,
        )}
      >
        {RATINGS.map((rating) => (
          <ToggleGroupItem
            key={rating}
            value={rating}
            aria-label={getSentimentLabel(rating)}
            className={cn(
              "border-border text-muted-foreground flex h-auto flex-1 flex-col items-center gap-[8px] rounded-[12px] border px-[16px] py-[14px] transition-[background-color,border-color,color,box-shadow]",
              "hover:border-primary/30 hover:bg-primary/5 hover:text-foreground",
              "data-[state=on]:border-primary/70 data-[state=on]:bg-primary/10 data-[state=on]:text-foreground data-[state=on]:ring-primary/70 data-[state=on]:ring-2",
              "data-[state=on]:hover:border-primary data-[state=on]:hover:bg-primary/15 data-[state=on]:hover:text-foreground",
            )}
          >
            <span className="text-[24px] leading-[28px]" aria-hidden="true">
              {getSentimentEmoji(rating)}
            </span>
            <span className="text-[12px] leading-[16px] font-medium">
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
