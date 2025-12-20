import * as React from "react";

import { Label } from "@/components/ui/label";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";
import {
  SENTIMENT_CONFIG,
  type SentimentRating,
} from "@/types/agent-feedback";

const RATING_ORDER: SentimentRating[] = ["unhappy", "neutral", "happy"];

interface EmojiRatingSelectorProps {
  /** Currently selected rating */
  value: SentimentRating;
  /** Callback when rating changes */
  onChange: (rating: SentimentRating) => void;
  /** Optional additional class names */
  className?: string;
  /** Whether the selector is disabled */
  disabled?: boolean;
}

/**
 * Large emoji button group for selecting overall sentiment rating.
 * Built on shadcn ToggleGroup for proper accessibility and keyboard navigation.
 */
export function EmojiRatingSelector({
  value,
  onChange,
  className,
  disabled = false,
}: EmojiRatingSelectorProps): React.ReactElement {
  const handleValueChange = (newValue: string): void => {
    // ToggleGroup returns empty string when deselecting, but we always want a selection
    if (newValue && RATING_ORDER.includes(newValue as SentimentRating)) {
      onChange(newValue as SentimentRating);
    }
  };

  return (
    <ToggleGroup
      type="single"
      value={value}
      onValueChange={handleValueChange}
      disabled={disabled}
      className={cn("flex items-center justify-center gap-4", className)}
      aria-label="Overall rating"
    >
      {RATING_ORDER.map((rating) => {
        const config = SENTIMENT_CONFIG[rating];
        const isSelected = value === rating;

        return (
          <ToggleGroupItem
            key={rating}
            value={rating}
            aria-label={config.label}
            className={cn(
              // Layout: vertical stack with emoji on top, label below
              "flex h-auto flex-col items-center gap-2 rounded-xl p-4",
              // Emoji sizing via first-child selector
              "[&>:first-child]:text-4xl [&>:first-child]:leading-none",
              // Transitions and interactions
              "transition-all duration-200",
              "hover:scale-105 active:scale-95",
              // Default state styling
              "bg-muted/50 text-muted-foreground",
              "hover:bg-muted hover:text-foreground",
              // Selected state with sentiment-specific colors
              isSelected && [
                config.bgClass,
                "ring-2 ring-current",
                config.colorClass,
              ],
            )}
          >
            {config.emoji}
            <Label
              className={cn(
                "pointer-events-none transition-colors",
                isSelected ? config.colorClass : "text-muted-foreground",
              )}
              size="sm"
              weight="medium"
            >
              {config.label}
            </Label>
          </ToggleGroupItem>
        );
      })}
    </ToggleGroup>
  );
}
