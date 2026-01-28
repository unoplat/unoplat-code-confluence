import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";

import type { SentimentRating } from "../schema";
import { getSentimentEmoji, getSentimentLabel } from "../utils";

interface MiniEmojiSelectorProps {
  /** Currently selected rating value (can be null for unrated) */
  value: SentimentRating | null;
  /** Callback when rating selection changes */
  onChange: (rating: SentimentRating | null) => void;
  /** Optional className for container */
  className?: string;
}

const RATINGS: SentimentRating[] = ["happy", "neutral", "unhappy"];

/**
 * Compact emoji-based sentiment rating selector for per-agent ratings
 *
 * Similar to EmojiRatingSelector but with smaller dimensions for use
 * in collapsible per-agent rating sections. Allows deselection (null value).
 */
export function MiniEmojiSelector({
  value,
  onChange,
  className,
}: MiniEmojiSelectorProps): React.ReactElement {
  return (
    <ToggleGroup
      type="single"
      value={value ?? ""}
      onValueChange={(newValue) => {
        // Allow deselection by passing null when value is empty
        onChange(newValue ? (newValue as SentimentRating) : null);
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
            "data-[state=on]:bg-primary/10 data-[state=on]:ring-primary data-[state=on]:ring-1",
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
