import type { RepositoryAgentEvent } from "@/features/repository-agent-snapshots/schema";
import type { AgentGroup } from "@/types/agent-events";

// Re-export AgentGroup for convenience
export type { AgentGroup } from "@/types/agent-events";

/**
 * Extensible enum-like constant for agent types.
 * Add new agents here as they are introduced.
 */
export const AgentType = {
  PROJECT_CONFIGURATION: "project_configuration_agent",
  DEVELOPMENT_WORKFLOW: "development_workflow_agent",
  BUSINESS_LOGIC_DOMAIN: "business_logic_domain_agent",
  // Future agents can be added here
} as const;

export type AgentTypeValue = (typeof AgentType)[keyof typeof AgentType];

/**
 * Registry mapping agent IDs to display metadata.
 * Order determines display sequence in the UI.
 */
export const AGENT_REGISTRY: Record<
  AgentTypeValue,
  { displayName: string; order: number }
> = {
  [AgentType.PROJECT_CONFIGURATION]: {
    displayName: "Project Configuration",
    order: 1,
  },
  [AgentType.DEVELOPMENT_WORKFLOW]: {
    displayName: "Development Workflow",
    order: 2,
  },
  [AgentType.BUSINESS_LOGIC_DOMAIN]: {
    displayName: "Business Logic Domain",
    order: 3,
  },
};

/**
 * Get human-readable display name for an agent.
 * Falls back to the raw agent ID if not in registry.
 */
export function getAgentDisplayName(agentId: string): string {
  const registryEntry = AGENT_REGISTRY[agentId as AgentTypeValue];
  if (registryEntry) {
    return registryEntry.displayName;
  }
  // Fallback: Convert snake_case to Title Case
  return agentId
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * Get the sort order for an agent.
 * Unknown agents are sorted to the end.
 */
function getAgentOrder(agentId: string): number {
  const registryEntry = AGENT_REGISTRY[agentId as AgentTypeValue];
  return registryEntry?.order ?? 999;
}

/**
 * Determine if an agent has completed based on its events.
 * An agent is considered complete if it has a "result" phase event.
 */
export function getAgentStatus(
  events: RepositoryAgentEvent[],
): "running" | "completed" {
  const hasResultPhase = events.some((event) => event.phase === "result");
  return hasResultPhase ? "completed" : "running";
}

/**
 * Truncate a message to a maximum length.
 * Returns the truncated text and whether truncation occurred.
 */
export function truncateMessage(
  message: string,
  maxLength: number = 50,
): { text: string; isTruncated: boolean } {
  if (message.length <= maxLength) {
    return { text: message, isTruncated: false };
  }
  return {
    text: message.slice(0, maxLength) + "...",
    isTruncated: true,
  };
}

/**
 * Group events by agent name and return sorted agent groups.
 * Only returns groups that have at least one event.
 */
export function groupEventsByAgent(
  events: RepositoryAgentEvent[],
): AgentGroup[] {
  // Group events by agent ID
  const groupsMap = new Map<string, RepositoryAgentEvent[]>();

  for (const event of events) {
    const agentId = event.event;
    const existingEvents = groupsMap.get(agentId) ?? [];
    existingEvents.push(event);
    groupsMap.set(agentId, existingEvents);
  }

  // Convert to AgentGroup array
  const groups: AgentGroup[] = [];

  for (const [agentId, agentEvents] of groupsMap) {
    groups.push({
      agentId,
      displayName: getAgentDisplayName(agentId),
      events: agentEvents,
      status: getAgentStatus(agentEvents),
      eventCount: agentEvents.length,
    });
  }

  // Sort by registry order
  groups.sort((a, b) => getAgentOrder(a.agentId) - getAgentOrder(b.agentId));

  return groups;
}
