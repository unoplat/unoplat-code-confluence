import React from "react";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { AgentGroupHeaderProps } from "@/types/agent-events";

function getStatusIcon(status: AgentGroupHeaderProps["group"]["status"]): React.ReactElement {
  if (status === "completed") {
    return <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />;
  }

  if (status === "pending") {
    return <Circle className="h-4 w-4 shrink-0 text-muted-foreground/60" />;
  }

  return <Loader2 className="h-4 w-4 shrink-0 animate-spin text-primary" />;
}

function getStatusVariant(
  status: AgentGroupHeaderProps["group"]["status"],
): "completed" | "outline" | "secondary" {
  if (status === "completed") {
    return "completed";
  }

  if (status === "pending") {
    return "outline";
  }

  return "secondary";
}

function getStatusLabel(status: AgentGroupHeaderProps["group"]["status"]): string {
  if (status === "completed") {
    return "COMPLETED";
  }

  if (status === "pending") {
    return "PENDING";
  }

  return "RUNNING";
}

export function AgentGroupHeader({
  group,
}: AgentGroupHeaderProps): React.ReactElement {
  return (
    <header className="flex min-w-0 flex-1 items-center gap-2 text-left">
      {getStatusIcon(group.status)}
      <span className="min-w-0 flex-1 truncate text-sm font-medium text-foreground">
        {group.displayName}
      </span>
      <Badge
        variant={getStatusVariant(group.status)}
        className="h-5 shrink-0 rounded-sm px-1.5 text-[11px] font-semibold uppercase tracking-wide"
      >
        {getStatusLabel(group.status)}
      </Badge>
    </header>
  );
}
