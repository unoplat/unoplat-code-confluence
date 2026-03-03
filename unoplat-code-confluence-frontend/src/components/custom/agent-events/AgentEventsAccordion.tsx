import React from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { AgentEventItem } from "@/components/custom/agent-events/AgentEventItem";
import { AgentGroupHeader } from "@/components/custom/agent-events/AgentGroupHeader";
import { ToolDetailModal } from "@/components/custom/agent-events/ToolDetailModal";
import { buildEventDisplayItems, groupEventsByAgent } from "@/lib/agent-events-utils";
import type { AgentEventsAccordionProps, ToolDetailItem } from "@/types/agent-events";

export function AgentEventsAccordion({
  events,
}: AgentEventsAccordionProps): React.ReactElement {
  const agentGroups = React.useMemo(() => groupEventsByAgent(events), [events]);
  const [detailItem, setDetailItem] = React.useState<ToolDetailItem | null>(
    null,
  );

  if (agentGroups.length === 0) {
    return (
      <p className="text-muted-foreground text-sm">No events available yet.</p>
    );
  }

  return (
    <>
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
              <section className="space-y-1.5 px-1">
                {buildEventDisplayItems(group.events).map((item) => (
                  <AgentEventItem
                    key={item.key}
                    item={item}
                    onViewDetails={setDetailItem}
                  />
                ))}
              </section>
            </AccordionContent>
          </AccordionItem>
        ))}
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
