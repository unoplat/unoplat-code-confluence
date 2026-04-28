import React from "react";
import { useVirtualizer } from "@tanstack/react-virtual";

import { AgentEventItem } from "@/components/custom/agent-events/AgentEventItem";
import { AgentGroupHeader } from "@/components/custom/agent-events/AgentGroupHeader";
import { ToolDetailModal } from "@/components/custom/agent-events/ToolDetailModal";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ScrollArea } from "@/components/ui/scroll-area";
import { buildEventDisplayItems, groupEventsByAgent } from "@/lib/agent-events-utils";
import type { RepositoryAgentEvent } from "@/features/repository-agent-snapshots/schema";
import type { AgentEventsAccordionProps, ToolDetailItem } from "@/types/agent-events";

const ROW_ESTIMATE_PX = 96;
const ROW_OVERSCAN = 5;
const NEAR_BOTTOM_ROW_TOLERANCE = 2;

interface VirtualizedAgentGroupEventsProps {
  events: RepositoryAgentEvent[];
  onViewDetails: (item: ToolDetailItem) => void;
}

function VirtualizedAgentGroupEvents({
  events,
  onViewDetails,
}: VirtualizedAgentGroupEventsProps): React.ReactElement {
  const items = React.useMemo(() => buildEventDisplayItems(events), [events]);
  const viewportRef = React.useRef<HTMLDivElement | null>(null);

  const rowVirtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => viewportRef.current,
    estimateSize: () => ROW_ESTIMATE_PX,
    overscan: ROW_OVERSCAN,
    getItemKey: (index) => items[index]?.key ?? index,
    useFlushSync: false,
  });

  const previousItemsCountRef = React.useRef<number>(0);
  const isNearBottomRef = React.useRef<boolean>(true);
  const itemsCountRef = React.useRef<number>(items.length);

  React.useLayoutEffect(() => {
    itemsCountRef.current = items.length;
  }, [items.length]);

  React.useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) {
      return undefined;
    }

    function handleScroll(): void {
      const virtualItems = rowVirtualizer.getVirtualItems();
      const lastVisible = virtualItems[virtualItems.length - 1];
      const totalCount = itemsCountRef.current;

      if (totalCount === 0 || !lastVisible) {
        isNearBottomRef.current = true;
        return;
      }

      isNearBottomRef.current =
        lastVisible.index >= totalCount - 1 - NEAR_BOTTOM_ROW_TOLERANCE;
    }

    viewport.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      viewport.removeEventListener("scroll", handleScroll);
    };
  }, [rowVirtualizer]);

  React.useEffect(() => {
    const previousCount = previousItemsCountRef.current;
    previousItemsCountRef.current = items.length;

    if (items.length === 0) {
      return undefined;
    }

    const isInitialMount = previousCount === 0;
    const grew = items.length > previousCount;
    const shouldFollow = isInitialMount || (grew && isNearBottomRef.current);

    if (!shouldFollow) {
      return undefined;
    }

    const targetIndex = items.length - 1;
    const frameId = requestAnimationFrame(() => {
      rowVirtualizer.scrollToIndex(targetIndex, { align: "end" });
      isNearBottomRef.current = true;
    });

    return () => {
      cancelAnimationFrame(frameId);
    };
  }, [items.length, rowVirtualizer]);

  if (items.length === 0) {
    return (
      <p className="text-muted-foreground text-xs">No events recorded yet.</p>
    );
  }

  const virtualRows = rowVirtualizer.getVirtualItems();

  return (
    <ScrollArea
      className="h-72 w-full"
      viewportRef={viewportRef}
      viewportClassName="[overflow-anchor:none]"
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          height: `${rowVirtualizer.getTotalSize()}px`,
        }}
      >
        {virtualRows.map((virtualRow) => {
          const item = items[virtualRow.index];
          if (!item) {
            return null;
          }

          return (
            <div
              key={virtualRow.key}
              data-index={virtualRow.index}
              ref={rowVirtualizer.measureElement}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                transform: `translateY(${virtualRow.start}px)`,
                paddingBottom: "8px",
              }}
            >
              <AgentEventItem item={item} onViewDetails={onViewDetails} />
            </div>
          );
        })}
      </div>
    </ScrollArea>
  );
}

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
                <VirtualizedAgentGroupEvents
                  events={group.events}
                  onViewDetails={setDetailItem}
                />
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
