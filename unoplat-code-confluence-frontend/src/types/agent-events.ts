import type { RepositoryAgentEvent } from "@/features/repository-agent-snapshots/schema";

/**
 * Represents a group of events for a single agent.
 */
export interface AgentGroup {
  agentId: string;
  displayName: string;
  events: RepositoryAgentEvent[];
  status: "pending" | "running" | "completed";
  eventCount: number;
}

/**
 * Props for the main AgentEventsAccordion component.
 */
export interface AgentEventsAccordionProps {
  events: RepositoryAgentEvent[];
  completedNamespaces: string[];
}

/**
 * Tool detail item payload used by Flow 2 detail modal.
 */
export interface ToolDetailItem {
  callEvent?: RepositoryAgentEvent;
  resultEvent?: RepositoryAgentEvent;
}

/**
 * Props for the Flow 2 ToolDetailModal component.
 */
export interface ToolDetailModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  item: ToolDetailItem | null;
}

/**
 * Display model for event timeline rows.
 * Tool calls/results can be rendered as a single paired item.
 */
export interface AgentEventSingleDisplayItem {
  type: "single";
  key: string;
  event: RepositoryAgentEvent;
}

export interface AgentEventToolPairDisplayItem {
  type: "tool-pair";
  key: string;
  callEvent: RepositoryAgentEvent;
  resultEvent?: RepositoryAgentEvent;
}

export type AgentEventDisplayItem =
  | AgentEventSingleDisplayItem
  | AgentEventToolPairDisplayItem;

/**
 * Props for the AgentEventItem component.
 */
export interface AgentEventItemProps {
  item: AgentEventDisplayItem;
  onViewDetails?: (item: ToolDetailItem) => void;
}

/**
 * Props for the AgentGroupHeader component.
 */
export interface AgentGroupHeaderProps {
  group: AgentGroup;
}
