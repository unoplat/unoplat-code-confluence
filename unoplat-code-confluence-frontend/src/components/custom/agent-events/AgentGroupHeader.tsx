import React from "react";
import { CheckCircle, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { AgentGroupHeaderProps } from "@/types/agent-events";

export function AgentGroupHeader({
  group,
}: AgentGroupHeaderProps): React.ReactElement {
  const isCompleted = group.status === "completed";

  return (
    <header className="flex flex-1 items-center gap-2">
      {isCompleted ? (
        <CheckCircle className="text-success h-4 w-4 shrink-0" />
      ) : (
        <Loader2 className="text-primary h-4 w-4 shrink-0 animate-spin" />
      )}
      <span className="flex-1 text-left text-sm font-medium">
        {group.displayName}
      </span>
      <Badge variant="secondary" className="ml-auto">
        {group.eventCount} {group.eventCount === 1 ? "event" : "events"}
      </Badge>
    </header>
  );
}
