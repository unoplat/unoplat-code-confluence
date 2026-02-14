import React from "react";
import { Wrench, FileText, CheckCircle, Circle } from "lucide-react";
import { ToolResultExpander } from "./ToolResultExpander";
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

export function AgentEventItem({
  item,
}: AgentEventItemProps): React.ReactElement {
  if (item.type === "tool-pair") {
    const callConfig = PHASE_CONFIG["tool.call"];
    const CallIcon = callConfig.icon;
    const callMessage = item.callEvent.message ?? item.callEvent.event;
    const resultMessage = item.resultEvent?.message ?? item.resultEvent?.event;

    return (
      <article className="space-y-1.5 text-xs">
        <div className="flex items-start gap-2">
          <CallIcon
            className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${callConfig.iconClassName}`}
          />
          <span className="text-muted-foreground break-all whitespace-pre-wrap">
            {callMessage}
          </span>
        </div>
        <div className="ml-5">
          {resultMessage ? (
            <ToolResultExpander message={resultMessage} />
          ) : (
            <span className="text-muted-foreground">Waiting for tool result...</span>
          )}
        </div>
      </article>
    );
  }

  const phase = item.event.phase as PhaseType | null;
  const config = phase
    ? (PHASE_CONFIG[phase] ?? DEFAULT_PHASE_CONFIG)
    : DEFAULT_PHASE_CONFIG;
  const Icon = config.icon;
  const message = item.event.message ?? item.event.event;

  const isToolResult = phase === "tool.result";

  return (
    <article className="flex items-start gap-2 text-xs">
      <Icon className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${config.iconClassName}`} />
      {isToolResult ? (
        <ToolResultExpander message={message} />
      ) : (
        <span className="text-muted-foreground break-all whitespace-pre-wrap">
          {message}
        </span>
      )}
    </article>
  );
}
