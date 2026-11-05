import React from "react";
import { Wrench, FileText, CheckCircle, Circle, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { RepositoryAgentEvent } from "@/features/repository-agent-snapshots/schema";
import type { AgentEventItemProps } from "@/types/agent-events";

type PhaseType = "tool.call" | "tool.result" | "result";

interface PhaseConfig {
  icon: React.ElementType;
  iconClassName: string;
}

const PHASE_CONFIG: Record<PhaseType, PhaseConfig> = {
  "tool.call": {
    icon: Wrench,
    iconClassName: "text-muted-foreground",
  },
  "tool.result": {
    icon: FileText,
    iconClassName: "text-muted-foreground",
  },
  result: {
    icon: CheckCircle,
    iconClassName: "text-success",
  },
};

// Static text by phase. Historical message values can hold generated previews.
const PHASE_MESSAGES: Record<string, string> = {
  "tool.call": "Tool call started",
  "tool.result": "Tool call finished",
  result: "Agent step completed",
};

const DEFAULT_PHASE_CONFIG: PhaseConfig = {
  icon: Circle,
  iconClassName: "text-muted-foreground",
};

function getToolName(callEvent: RepositoryAgentEvent): string {
  if (
    typeof callEvent.tool_name === "string" &&
    callEvent.tool_name.trim().length > 0
  ) {
    return callEvent.tool_name;
  }

  return callEvent.event;
}

export function AgentEventItem({
  item,
}: AgentEventItemProps): React.ReactElement {
  if (item.type === "tool-pair") {
    const hasResult = Boolean(item.resultEvent);

    return (
      <article className="grid grid-cols-[20px_minmax(0,1fr)] gap-x-2 gap-y-1 text-xs">
        <div className="relative row-span-2">
          <span className="bg-primary absolute top-3 left-1/2 h-2 w-2 -translate-x-1/2 rounded-full" />
          <span
            className={cn(
              "absolute top-4 bottom-4 left-1/2 -translate-x-1/2",
              hasResult
                ? "bg-success/60 w-0.5"
                : "border-border/90 w-0 border-l border-dashed",
            )}
          />
          <span
            className={cn(
              "absolute bottom-3 left-1/2 h-2 w-2 -translate-x-1/2 rounded-full",
              hasResult ? "bg-success" : "bg-border",
            )}
          />
        </div>

        <div className="border-secondary/70 bg-secondary/40 col-start-2 flex h-8 min-w-0 items-center gap-1.5 overflow-hidden rounded-md border px-2.5">
          <Badge
            variant="secondary"
            className="h-[14px] shrink-0 rounded-sm border-0 px-1.5 text-[11px] font-medium tracking-wide uppercase"
          >
            CALL
          </Badge>
          <span className="text-foreground min-w-0 flex-1 truncate font-mono text-xs font-medium">
            {getToolName(item.callEvent)}
          </span>
        </div>

        {item.resultEvent ? (
          <div className="border-success/30 bg-success/10 col-start-2 flex h-8 min-w-0 items-center gap-1.5 overflow-hidden rounded-md border px-2.5">
            <Badge
              variant="completed"
              className="h-[14px] shrink-0 rounded-sm border-0 px-1.5 text-[11px] font-medium tracking-wide uppercase"
            >
              RESULT
            </Badge>
            <span className="text-muted-foreground min-w-0 flex-1 truncate text-xs">
              Tool call finished
            </span>
          </div>
        ) : (
          <div className="border-border bg-muted/40 dark:bg-muted/30 col-start-2 flex h-8 min-w-0 items-center gap-1.5 overflow-hidden rounded-md border border-dashed px-2.5">
            <Loader2 className="text-muted-foreground h-3 w-3 shrink-0 animate-spin" />
            <span className="text-muted-foreground text-xs">
              Awaiting result...
            </span>
          </div>
        )}
      </article>
    );
  }

  const phase = item.event.phase as PhaseType | null;
  const config = phase
    ? (PHASE_CONFIG[phase] ?? DEFAULT_PHASE_CONFIG)
    : DEFAULT_PHASE_CONFIG;
  const Icon = config.icon;
  const message = PHASE_MESSAGES[item.event.phase] ?? item.event.event;

  return (
    <article className="flex items-start gap-2 text-xs">
      <Icon className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${config.iconClassName}`} />
      <span className="text-muted-foreground break-all whitespace-pre-wrap">
        {message}
      </span>
    </article>
  );
}
