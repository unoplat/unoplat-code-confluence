import { Bug, Lightbulb, MessageCircle } from "lucide-react";

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";

import { type AppFeedbackCategory, CATEGORY_LABELS } from "../schema";

interface FeedbackCategorySelectorProps {
  value: AppFeedbackCategory | undefined;
  onChange: (category: AppFeedbackCategory) => void;
  className?: string;
}

const CATEGORIES: {
  value: AppFeedbackCategory;
  icon: React.ReactElement;
}[] = [
  { value: "bug_report", icon: <Bug className="h-6 w-6" /> },
  {
    value: "feature_request",
    icon: <Lightbulb className="h-6 w-6" />,
  },
  { value: "general", icon: <MessageCircle className="h-6 w-6" /> },
];

export function FeedbackCategorySelector({
  value,
  onChange,
  className,
}: FeedbackCategorySelectorProps): React.ReactElement {
  return (
    <ToggleGroup
      type="single"
      value={value}
      onValueChange={(newValue) => {
        if (newValue) {
          onChange(newValue as AppFeedbackCategory);
        }
      }}
      className={cn("flex w-full items-center gap-[10px]", className)}
    >
      {CATEGORIES.map((cat) => (
        <ToggleGroupItem
          key={cat.value}
          value={cat.value}
          aria-label={CATEGORY_LABELS[cat.value]}
          className={cn(
            "border-border text-muted-foreground flex h-auto flex-1 flex-col items-center gap-[8px] rounded-[12px] border px-[16px] py-[14px] transition-[background-color,border-color,color,box-shadow]",
            "hover:border-primary/30 hover:bg-primary/5 hover:text-foreground",
            "data-[state=on]:border-primary/70 data-[state=on]:bg-primary/10 data-[state=on]:text-foreground data-[state=on]:ring-primary/70 data-[state=on]:ring-2",
            "data-[state=on]:hover:border-primary data-[state=on]:hover:bg-primary/15 data-[state=on]:hover:text-foreground",
          )}
        >
          {cat.icon}
          <span className="text-[12px] leading-[16px] font-medium">
            {CATEGORY_LABELS[cat.value]}
          </span>
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
