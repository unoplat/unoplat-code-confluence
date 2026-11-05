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
}

/**
 * Props for the AgentGroupHeader component.
 */
export interface AgentGroupHeaderProps {
  group: AgentGroup;
}
