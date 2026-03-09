import React from "react";

import { AgentEventItem } from "@/components/custom/agent-events/AgentEventItem";
import { AgentGroupHeader } from "@/components/custom/agent-events/AgentGroupHeader";
import { ToolDetailModal } from "@/components/custom/agent-events/ToolDetailModal";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { buildEventDisplayItems, groupEventsByAgent } from "@/lib/agent-events-utils";
import type { AgentEventsAccordionProps, ToolDetailItem } from "@/types/agent-events";

export function AgentEventsAccordion({
  events,
  completedNamespaces,
}: AgentEventsAccordionProps): React.ReactElement {
  const agentGroups = React.useMemo(
    () => groupEventsByAgent(events, completedNamespaces),
    [events, completedNamespaces],
  );
  const [detailItem, setDetailItem] = React.useState<ToolDetailItem | null>(null);
  const [expandedGroups, setExpandedGroups] = React.useState<string[]>([]);

  React.useEffect(() => {
    const nextGroupIds = agentGroups.map((group) => group.agentId);

    setExpandedGroups((currentExpandedGroups) =>
      currentExpandedGroups.filter((groupId) => nextGroupIds.includes(groupId)),
    );
  }, [agentGroups]);

  if (agentGroups.length === 0) {
    return (
      <p className="text-muted-foreground px-3 py-3 text-sm">
        No events available yet.
      </p>
    );
  }

  return (
    <>
      <Accordion
        type="multiple"
        value={expandedGroups}
        onValueChange={setExpandedGroups}
        className="w-full"
      >
        {agentGroups.map((group) => {
          if (group.eventCount === 0) {
            return null;
          }

          const items = buildEventDisplayItems(group.events);

          return (
            <AccordionItem
              key={group.agentId}
              value={group.agentId}
              className="border-border border-b last:border-b-0"
            >
              <AccordionTrigger className="px-4 py-2.5 hover:no-underline">
                <AgentGroupHeader group={group} />
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-3 pt-1">
                <section className="space-y-2">
                  {items.map((item) => (
                    <AgentEventItem
                      key={item.key}
                      item={item}
                      onViewDetails={setDetailItem}
                    />
                  ))}
                </section>
              </AccordionContent>
            </AccordionItem>
          );
        })}
      </Accordion>

      <ToolDetailModal
        open={detailItem !== null}
        onOpenChange={(nextOpen) => {
          if (!nextOpen) {
            setDetailItem(null);
          }
        }}
        item={detailItem}
      />
    </>
  );
}
