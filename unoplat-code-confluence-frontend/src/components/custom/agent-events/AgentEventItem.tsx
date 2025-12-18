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
  event,
}: AgentEventItemProps): React.ReactElement {
  const phase = event.phase as PhaseType | null;
  const config = phase
    ? (PHASE_CONFIG[phase] ?? DEFAULT_PHASE_CONFIG)
    : DEFAULT_PHASE_CONFIG;
  const Icon = config.icon;
  const message = event.message ?? event.event;

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
