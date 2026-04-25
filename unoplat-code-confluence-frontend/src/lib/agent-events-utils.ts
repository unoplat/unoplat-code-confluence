import type { RepositoryAgentEvent } from "@/features/repository-agent-snapshots/schema";
import type { AgentEventDisplayItem, AgentGroup } from "@/types/agent-events";

// Re-export AgentGroup for convenience
export type { AgentGroup } from "@/types/agent-events";

/**
 * Extensible enum-like constant for agent types.
 * Add new agents here as they are introduced.
 */
export const AgentType = {
  DEVELOPMENT_WORKFLOW: "development_workflow_guide",
  DEPENDENCY: "dependency_guide",
  BUSINESS_DOMAIN: "business_domain_guide",
  APP_INTERFACE_VALIDATOR: "call_expression_validator",
  APP_INTERFACES: "app_interfaces_agent",
} as const;

/**
 * Maps item-level agent names to their canonical parent agent.
 * Used to consolidate related events into a single display group.
 */
const AGENT_ALIASES: Record<string, string> = {
  app_interface_validator: "call_expression_validator",
  dependency_guide_item: "dependency_guide",
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
  [AgentType.DEVELOPMENT_WORKFLOW]: {
    displayName: "Development Workflow Guide",
    order: 1,
  },
  [AgentType.DEPENDENCY]: {
    displayName: "Dependency Guide",
    order: 2,
  },
  [AgentType.BUSINESS_DOMAIN]: {
    displayName: "Business Domain Guide",
    order: 3,
  },
  [AgentType.APP_INTERFACE_VALIDATOR]: {
    displayName: "App Interface Validator",
    order: 4,
  },
  [AgentType.APP_INTERFACES]: {
    displayName: "App Interfaces",
    order: 5,
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
 * Return the latest event by event_id.
 */
function getLatestEvent(
  events: RepositoryAgentEvent[],
): RepositoryAgentEvent | null {
  if (events.length === 0) {
    return null;
  }

  let latestEvent = events[0] ?? null;

  for (const event of events) {
    if (!latestEvent || event.event_id > latestEvent.event_id) {
      latestEvent = event;
    }
  }

  return latestEvent;
}

/**
 * Determine an agent group's runtime status from its newest event.
 *
 * Why newest event wins:
 * - Historical result events can exist while the same group continues streaming
 *   (for example, section updater events after completion signals, or repeated
 *   validator runs).
 * - Status should show running whenever newer non-result activity is present.
 *
 * @param events - All events in the agent group
 * @param canonicalAgentId - Optional canonical agent ID for grouped agents
 * @param isCompleted - Optional completion signal from completed_namespaces
 */
export function getAgentStatus(
  events: RepositoryAgentEvent[],
  canonicalAgentId?: string,
  isCompleted?: boolean,
): "pending" | "running" | "completed" {
  if (events.length === 0) {
    return isCompleted ? "completed" : "pending";
  }

  const latestEvent = getLatestEvent(events);
  if (!latestEvent) {
    return isCompleted ? "completed" : "pending";
  }

  if (latestEvent.phase !== "result") {
    return "running";
  }

  if (isCompleted) {
    return "completed";
  }

  if (!canonicalAgentId) {
    return "completed";
  }

  return latestEvent.event === canonicalAgentId ? "completed" : "running";
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

function getToolCallId(event: RepositoryAgentEvent): string | null {
  const toolCallId = event.tool_call_id;
  if (typeof toolCallId !== "string" || toolCallId.trim().length === 0) {
    return null;
  }
  return toolCallId;
}

/**
 * Build display items by pairing tool calls with tool results.
 * Pairing uses strict tool_call_id matching and preserves event order.
 */
export function buildEventDisplayItems(
  events: RepositoryAgentEvent[],
): AgentEventDisplayItem[] {
  const sortedEvents = [...events].sort((a, b) => a.event_id - b.event_id);
  const items: AgentEventDisplayItem[] = [];

  const resultEventsByToolCallId = new Map<string, RepositoryAgentEvent[]>();
  for (const event of sortedEvents) {
    if (event.phase !== "tool.result") {
      continue;
    }

    const toolCallId = getToolCallId(event);
    if (!toolCallId) {
      continue;
    }

    const existingResults = resultEventsByToolCallId.get(toolCallId) ?? [];
    existingResults.push(event);
    resultEventsByToolCallId.set(toolCallId, existingResults);
  }

  const consumedResultIds = new Set<number>();

  for (const event of sortedEvents) {
    if (event.phase === "tool.call") {
      const toolCallId = getToolCallId(event);
      if (!toolCallId) {
        items.push({
          type: "single",
          key: `event-${event.event_id}`,
          event,
        });
        continue;
      }

      const candidateResults = resultEventsByToolCallId.get(toolCallId) ?? [];
      let matchedResultEvent: RepositoryAgentEvent | undefined;

      for (const candidate of candidateResults) {
        if (consumedResultIds.has(candidate.event_id)) {
          continue;
        }

        if (candidate.event_id > event.event_id) {
          matchedResultEvent = candidate;
          consumedResultIds.add(candidate.event_id);
          break;
        }
      }

      items.push({
        type: "tool-pair",
        key: matchedResultEvent
          ? `tool-pair-${event.event_id}-${matchedResultEvent.event_id}`
          : `tool-pair-${event.event_id}`,
        callEvent: event,
        resultEvent: matchedResultEvent,
      });
      continue;
    }

    if (
      event.phase === "tool.result" &&
      consumedResultIds.has(event.event_id)
    ) {
      continue;
    }

    items.push({
      type: "single",
      key: `event-${event.event_id}`,
      event,
    });
  }

  return items;
}

/**
 * Group events by agent name and return sorted agent groups.
 * Only returns groups that have at least one event — agents that never
 * emitted any events (not applicable for this run) are excluded.
 *
 * Events from aliased agents (e.g., "dependency_guide_item") are
 * consolidated into their canonical parent agent group (e.g., "dependency_guide").
 */
export function groupEventsByAgent(
  events: RepositoryAgentEvent[],
  completedNamespaces?: string[],
): AgentGroup[] {
  const groupsMap = new Map<string, RepositoryAgentEvent[]>();
  const completedSet = new Set(completedNamespaces ?? []);

  for (const event of events) {
    const canonicalAgentId = resolveAgentId(event.event);
    const existingEvents = groupsMap.get(canonicalAgentId) ?? [];
    existingEvents.push(event);
    groupsMap.set(canonicalAgentId, existingEvents);
  }

  const groups: AgentGroup[] = [];

  for (const agentId of Object.keys(AGENT_REGISTRY)) {
    const agentEvents = groupsMap.get(agentId) ?? [];
    groups.push({
      agentId,
      displayName: getAgentDisplayName(agentId),
      events: agentEvents,
      status: getAgentStatus(agentEvents, agentId, completedSet.has(agentId)),
      eventCount: agentEvents.length,
    });
    groupsMap.delete(agentId);
  }

  for (const [agentId, agentEvents] of groupsMap) {
    groups.push({
      agentId,
      displayName: getAgentDisplayName(agentId),
      events: agentEvents,
      status: getAgentStatus(agentEvents, agentId, completedSet.has(agentId)),
      eventCount: agentEvents.length,
    });
  }

  groups.sort((a, b) => getAgentOrder(a.agentId) - getAgentOrder(b.agentId));

  return groups;
}

export interface AgentGroupSummaryCounts {
  completed: number;
  pending: number;
  running: number;
  total: number;
}

export function getAgentGroupSummaryCounts(
  groups: AgentGroup[],
): AgentGroupSummaryCounts {
  let completed = 0;
  let pending = 0;
  let running = 0;

  for (const group of groups) {
    if (group.status === "completed") {
      completed += 1;
      continue;
    }

    if (group.status === "pending") {
      pending += 1;
      continue;
    }

    running += 1;
  }

  return {
    completed,
    pending,
    running,
    total: groups.length,
  };
}
