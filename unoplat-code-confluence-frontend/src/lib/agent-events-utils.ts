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
  DEPENDENCY_GUIDE: "dependency_guide_agent",
  BUSINESS_LOGIC_DOMAIN: "business_logic_domain_agent",
  // Future agents can be added here
} as const;

/**
 * Maps item-level agent names to their canonical parent agent.
 * Used to consolidate related events into a single display group.
 */
const AGENT_ALIASES: Record<string, string> = {
  dependency_guide_agent_item: "dependency_guide_agent",
};

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
  [AgentType.DEPENDENCY_GUIDE]: {
    displayName: "Dependency Guide",
    order: 3,
  },
  [AgentType.BUSINESS_LOGIC_DOMAIN]: {
    displayName: "Business Logic Domain",
    order: 4,
  },
};

/**
 * Resolves an agent ID to its canonical form.
 * If the agent has an alias, returns the canonical agent ID.
 * Otherwise returns the original agent ID.
 */
function resolveAgentId(eventAgentId: string): string {
  return AGENT_ALIASES[eventAgentId] ?? eventAgentId;
}

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
 *
 * For grouped agents (those with aliases), completion is determined by
 * checking if the canonical agent has emitted a "result" phase event,
 * not the aliased item-level events.
 *
 * @param events - All events in the agent group
 * @param canonicalAgentId - Optional canonical agent ID for grouped agents
 */
export function getAgentStatus(
  events: RepositoryAgentEvent[],
  canonicalAgentId?: string,
): "running" | "completed" {
  const hasResultPhase = events.some(
    (event) =>
      event.phase === "result" &&
      // For grouped agents, only count result from the canonical agent
      (!canonicalAgentId || event.event === canonicalAgentId),
  );
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
 *
 * Events from aliased agents (e.g., "dependency_guide_agent_item") are
 * consolidated into their canonical parent agent group (e.g., "dependency_guide_agent").
 */
export function groupEventsByAgent(
  events: RepositoryAgentEvent[],
): AgentGroup[] {
  // Group events by canonical agent ID (resolving aliases)
  const groupsMap = new Map<string, RepositoryAgentEvent[]>();

  for (const event of events) {
    const canonicalAgentId = resolveAgentId(event.event);
    const existingEvents = groupsMap.get(canonicalAgentId) ?? [];
    existingEvents.push(event);
    groupsMap.set(canonicalAgentId, existingEvents);
  }

  // Convert to AgentGroup array
  const groups: AgentGroup[] = [];

  for (const [agentId, agentEvents] of groupsMap) {
    groups.push({
      agentId,
      displayName: getAgentDisplayName(agentId),
      events: agentEvents,
      // Pass canonicalAgentId so status checks canonical agent's result event
      status: getAgentStatus(agentEvents, agentId),
      eventCount: agentEvents.length,
    });
  }

  // Sort by registry order
  groups.sort((a, b) => getAgentOrder(a.agentId) - getAgentOrder(b.agentId));

  return groups;
}
