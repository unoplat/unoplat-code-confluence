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
 * Displays three emoji options (😊 😐 😞) as toggle buttons.
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
        // Only trigger onChange if a value is selected (prevent deselection)
        if (newValue) {
          onChange(newValue as SentimentRating);
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
  );
}
