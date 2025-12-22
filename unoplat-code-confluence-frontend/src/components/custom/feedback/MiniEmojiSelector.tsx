import * as React from "react";

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";
import {
  SENTIMENT_CONFIG,
  type SentimentRating,
} from "@/types/agent-feedback";

const RATING_ORDER: SentimentRating[] = ["unhappy", "neutral", "happy"];

interface MiniEmojiSelectorProps {
  /** Currently selected rating (null means no selection) */
  value: SentimentRating | null;
  /** Callback when rating changes */
  onChange: (rating: SentimentRating | null) => void;
  /** Optional additional class names */
  className?: string;
  /** Whether the selector is disabled */
  disabled?: boolean;
}

/**
 * Compact emoji selector for per-agent per-codebase ratings.
 * Icon-only design for use in dense grid layouts.
 * Built on shadcn ToggleGroup for accessibility and keyboard navigation.
 */
export function MiniEmojiSelector({
  value,
  onChange,
  className,
  disabled = false,
}: MiniEmojiSelectorProps): React.ReactElement {
  const handleValueChange = (newValue: string): void => {
    // Allow deselection (empty string) for optional per-agent ratings
    if (newValue === "") {
      onChange(null);
    } else if (RATING_ORDER.includes(newValue as SentimentRating)) {
      onChange(newValue as SentimentRating);
    }
  };

  return (
    <ToggleGroup
      type="single"
      value={value ?? ""}
      onValueChange={handleValueChange}
      disabled={disabled}
      className={cn("flex items-center gap-1", className)}
      aria-label="Agent rating"
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
              // Compact sizing
              "h-8 w-8 rounded-md p-0 text-lg",
              // Transitions
              "transition-all duration-150",
              "hover:scale-110 active:scale-95",
              // Default state
              "bg-transparent text-muted-foreground/60",
              "hover:bg-muted hover:text-muted-foreground",
              // Selected state with sentiment-specific colors
              isSelected && [
                config.bgClass,
                "ring-1 ring-current",
                config.colorClass,
                "text-opacity-100",
              ],
            )}
          >
            {config.emoji}
          </ToggleGroupItem>
        );
      })}
    </ToggleGroup>
  );
}
