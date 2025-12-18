import React from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { groupEventsByAgent } from "@/lib/agent-events-utils";
import { AgentGroupHeader } from "./AgentGroupHeader";
import { AgentEventItem } from "./AgentEventItem";
import type { AgentEventsAccordionProps } from "@/types/agent-events";

export function AgentEventsAccordion({
  events,
}: AgentEventsAccordionProps): React.ReactElement {
  const agentGroups = React.useMemo(() => groupEventsByAgent(events), [events]);

  if (agentGroups.length === 0) {
    return (
      <p className="text-muted-foreground text-sm">No events available yet.</p>
    );
  }

  return (
    <Accordion type="single" collapsible className="w-full space-y-2">
      {agentGroups.map((group) => (
        <AccordionItem
          key={group.agentId}
          value={group.agentId}
          className="border-border rounded-md border"
        >
          <AccordionTrigger className="px-3 py-2 hover:no-underline">
            <AgentGroupHeader group={group} />
          </AccordionTrigger>
          <AccordionContent className="px-3 pb-3">
            <section className="space-y-1.5 pl-6">
              {group.events.map((event) => (
                <AgentEventItem key={event.id} event={event} />
              ))}
            </section>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
}
