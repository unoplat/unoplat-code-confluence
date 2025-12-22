import type { RepositoryAgentEvent } from "@/features/repository-agent-snapshots/schema";

/**
 * Represents a group of events for a single agent.
 */
export interface AgentGroup {
  agentId: string;
  displayName: string;
  events: RepositoryAgentEvent[];
  status: "running" | "completed";
  eventCount: number;
}

/**
 * Props for the main AgentEventsAccordion component.
 */
export interface AgentEventsAccordionProps {
  events: RepositoryAgentEvent[];
}

/**
 * Props for the ToolResultExpander component.
 */
export interface ToolResultExpanderProps {
  message: string;
  maxLength?: number;
}

/**
 * Props for the AgentEventItem component.
 */
export interface AgentEventItemProps {
  event: RepositoryAgentEvent;
}

/**
 * Props for the AgentGroupHeader component.
 */
export interface AgentGroupHeaderProps {
  group: AgentGroup;
}
