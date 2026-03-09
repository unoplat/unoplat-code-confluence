import React from "react";
import { Wrench, FileText, CheckCircle, Circle, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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

const DEFAULT_PHASE_CONFIG: PhaseConfig = {
  icon: Circle,
  iconClassName: "text-muted-foreground",
};

function stripToolResultPrefix(value: string): string {
  return value.replace(/^Tool result:\s*/, "");
}

function getToolName(callEvent: RepositoryAgentEvent): string {
  if (
    typeof callEvent.tool_name === "string" &&
    callEvent.tool_name.trim().length > 0
  ) {
    return callEvent.tool_name;
  }

  if (
    typeof callEvent.message === "string" &&
    callEvent.message.trim().length > 0
  ) {
    return callEvent.message.replace(/^Calling\s+/, "");
  }

  return callEvent.event;
}

function stringifyUnknown(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  if (value === null) {
    return "null";
  }

  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function compactHintValue(value: string, maxLength: number = 28): string {
  if (value.length <= maxLength) {
    return value;
  }

  const pathSegments = value.split("/").filter((segment) => segment.length > 0);
  if (pathSegments.length >= 2) {
    const tailHint = `.../${pathSegments.slice(-2).join("/")}`;
    if (tailHint.length <= maxLength) {
      return tailHint;
    }
  }

  return `${value.slice(0, maxLength - 3)}...`;
}

function getCallHint(callEvent: RepositoryAgentEvent): string | null {
  const toolArgs = callEvent.tool_args;
  if (!toolArgs) {
    return null;
  }

  const firstEntry = Object.entries(toolArgs)[0];
  if (!firstEntry) {
    return null;
  }

  const [key, firstValue] = firstEntry;
  const compactValue = compactHintValue(stringifyUnknown(firstValue));

  if (key === "path" || key === "file_path" || key === "filepath") {
    return `path: ${compactValue}`;
  }

  return compactValue;
}

function getResultPreview(resultEvent: RepositoryAgentEvent): string {
  const rawContent =
    (typeof resultEvent.tool_result_content === "string" &&
    resultEvent.tool_result_content.length > 0
      ? resultEvent.tool_result_content
      : typeof resultEvent.message === "string"
        ? stripToolResultPrefix(resultEvent.message)
        : resultEvent.event) ?? "";

  if (rawContent.length <= 50) {
    return rawContent;
  }

  return `${rawContent.slice(0, 50)}...`;
}

export function AgentEventItem({
  item,
  onViewDetails,
}: AgentEventItemProps): React.ReactElement {
  if (item.type === "tool-pair") {
    const hasResult = Boolean(item.resultEvent);
    const callHint = getCallHint(item.callEvent);
    const resultPreview = item.resultEvent
      ? getResultPreview(item.resultEvent)
      : null;

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
          {callHint ? (
            <span className="bg-background/60 text-muted-foreground dark:bg-background/20 max-w-[160px] shrink-0 truncate rounded px-1.5 py-px font-mono text-[11px]">
              {callHint}
            </span>
          ) : null}
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
              {resultPreview || "-"}
            </span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="text-primary hover:text-primary/80 h-4 shrink-0 px-1 text-[11px] hover:bg-transparent"
              onClick={() => {
                onViewDetails?.({
                  callEvent: item.callEvent,
                  resultEvent: item.resultEvent,
                });
              }}
            >
              View details -&gt;
            </Button>
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
  const message = item.event.message ?? item.event.event;

  return (
    <article className="flex items-start gap-2 text-xs">
      <Icon className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${config.iconClassName}`} />
      <span className="text-muted-foreground break-all whitespace-pre-wrap">
        {message}
      </span>
    </article>
  );
}
