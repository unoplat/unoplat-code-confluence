import { ThumbsDown, ThumbsUp } from "lucide-react";

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";

import type { AgentSentimentRating } from "../schema";

interface ThumbsRatingSelectorProps {
  /** Currently selected rating value (can be null for unrated) */
  value: AgentSentimentRating | null;
  /** Callback when rating selection changes */
  onChange: (rating: AgentSentimentRating | null) => void;
  /** Optional className for container */
  className?: string;
}

const RATINGS: Array<{
  value: AgentSentimentRating;
  label: string;
  icon: typeof ThumbsUp;
}> = [
  { value: "happy", label: "Thumbs up", icon: ThumbsUp },
  { value: "unhappy", label: "Thumbs down", icon: ThumbsDown },
];

/**
 * Compact thumbs up/down rating selector for per-agent binary ratings.
 *
 * Uses ToggleGroup with variant="soft" and size="icon" for consistent
 * styling via the toggle variant system. The soft variant uses ring-inset
 * to avoid overflow clipping inside accordion containers.
 */
export function ThumbsRatingSelector({
  value,
  onChange,
  className,
}: ThumbsRatingSelectorProps): React.ReactElement {
  return (
    <ToggleGroup
      type="single"
      variant="soft"
      size="icon"
      value={value ?? ""}
      onValueChange={(newValue) => {
        onChange(newValue ? (newValue as AgentSentimentRating) : null);
      }}
      className={cn("shrink-0", className)}
    >
      {RATINGS.map((rating) => (
        <ToggleGroupItem
          key={rating.value}
          value={rating.value}
          aria-label={rating.label}
        >
          <rating.icon aria-hidden="true" />
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
