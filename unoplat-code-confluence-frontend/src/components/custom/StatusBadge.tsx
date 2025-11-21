import * as React from "react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type FeatureStatus = "alpha" | "beta";

export interface StatusBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  status: FeatureStatus;
}

const statusLabels: Record<FeatureStatus, string> = {
  alpha: "Alpha",
  beta: "Beta",
};

const statusDescriptions: Record<FeatureStatus, string> = {
  alpha: "Experimental feature - may have limited functionality or bugs",
  beta: "Testing feature - mostly stable but may change",
};

export function StatusBadge({
  status,
  className,
  title,
  ...props
}: StatusBadgeProps) {
  const label = statusLabels[status];
  const description = statusDescriptions[status];

  return (
    <Badge
      variant={status}
      className={cn(className)}
      title={title || description}
      {...props}
    >
      {label}
    </Badge>
  );
}

export { statusLabels, statusDescriptions };
