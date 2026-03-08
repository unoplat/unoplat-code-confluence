import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";

import type { SentimentRating } from "../schema";
import { getSentimentEmoji, getSentimentLabel } from "../utils";

interface EmojiRatingSelectorProps {
  /** Currently selected rating value */
  value: SentimentRating | undefined;
  /** Callback when rating selection changes */
  onChange: (rating: SentimentRating) => void;
  /** Optional className for container */
  className?: string;
}

const RATINGS: SentimentRating[] = ["happy", "neutral", "unhappy"];

/**
 * Emoji-based sentiment rating selector using shadcn ToggleGroup
 *
 * Displays three emoji options as toggle buttons.
 * Uses `type="single"` for mutually exclusive selection.
 */
export function EmojiRatingSelector({
  value,
  onChange,
  className,
}: EmojiRatingSelectorProps): React.ReactElement {
  return (
    <ToggleGroup
      type="single"
      value={value}
      onValueChange={(newValue) => {
        if (newValue) {
          onChange(newValue as SentimentRating);
        }
      }}
      className={cn(
        "flex w-full items-center justify-center gap-2.5 py-2",
        className,
      )}
    >
      {RATINGS.map((rating) => (
        <ToggleGroupItem
          key={rating}
          value={rating}
          aria-label={getSentimentLabel(rating)}
          className={cn(
            "border-border flex h-auto flex-1 flex-col items-center gap-[8px] rounded-[12px] border px-[16px] py-[14px]",
            "hover:bg-muted/50",
            "data-[state=on]:border-primary/30 data-[state=on]:bg-primary/10 data-[state=on]:ring-primary data-[state=on]:ring-2",
          )}
        >
          <span className="text-[24px] leading-[28px]" aria-hidden="true">
            {getSentimentEmoji(rating)}
          </span>
          <span className="text-muted-foreground text-xs font-medium">
            {getSentimentLabel(rating)}
          </span>
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
