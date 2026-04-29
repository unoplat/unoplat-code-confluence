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
import type {
  AgentEventDisplayItem,
  AgentEventsAccordionProps,
  ToolDetailItem,
} from "@/types/agent-events";

const ROW_ESTIMATE_PX = 96;
const ROW_OVERSCAN = 5;
const NEAR_BOTTOM_ROW_TOLERANCE = 2;

export interface OlderHistoryAnchor {
  groupId: string;
  anchorKey: string;
  fallbackEventIds: number[];
}

export interface AgentEventsAccordionHandle {
  captureOlderHistoryAnchors: () => OlderHistoryAnchor[];
  restoreOlderHistoryAnchors: (anchors: OlderHistoryAnchor[]) => void;
}

interface OlderHistoryItemAnchor {
  anchorKey: string;
  fallbackEventIds: number[];
}

interface VirtualizedAgentGroupEventsHandle {
  getFirstVisibleAnchor: () => OlderHistoryItemAnchor | null;
  restoreToAnchor: (anchor: OlderHistoryAnchor) => void;
}

type RegisterGroupHandle = (
  groupId: string,
  handle: VirtualizedAgentGroupEventsHandle | null,
) => void;

function getDisplayItemEventIds(item: AgentEventDisplayItem): number[] {
  if (item.type === "tool-pair") {
    return item.resultEvent
      ? [item.callEvent.event_id, item.resultEvent.event_id]
      : [item.callEvent.event_id];
  }

  return [item.event.event_id];
}

function getDisplayItemAnchor(
  item: AgentEventDisplayItem,
): OlderHistoryItemAnchor {
  return {
    anchorKey: item.key,
    fallbackEventIds: getDisplayItemEventIds(item),
  };
}

function findAnchorIndex(
  items: AgentEventDisplayItem[],
  anchor: OlderHistoryAnchor,
): number {
  const exactKeyIndex = items.findIndex((item) => item.key === anchor.anchorKey);
  if (exactKeyIndex !== -1) {
    return exactKeyIndex;
  }

  const fallbackEventIds = new Set(anchor.fallbackEventIds);
  if (fallbackEventIds.size === 0) {
    return -1;
  }

  return items.findIndex((item) =>
    getDisplayItemEventIds(item).some((eventId) =>
      fallbackEventIds.has(eventId),
    ),
  );
}

interface VirtualizedAgentGroupEventsProps {
  groupId: string;
  events: RepositoryAgentEvent[];
  onViewDetails: (item: ToolDetailItem) => void;
  registerHandle: RegisterGroupHandle;
}

function VirtualizedAgentGroupEvents({
  groupId,
  events,
  onViewDetails,
  registerHandle,
}: VirtualizedAgentGroupEventsProps): React.ReactElement {
  const items = React.useMemo(() => buildEventDisplayItems(events), [events]);
  const itemsRef = React.useRef<AgentEventDisplayItem[]>(items);
  itemsRef.current = items;
  const viewportRef = React.useRef<HTMLDivElement | null>(null);

  const rowVirtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => viewportRef.current,
    estimateSize: () => ROW_ESTIMATE_PX,
    overscan: ROW_OVERSCAN,
    getItemKey: (index) => items[index]?.key ?? index,
    useFlushSync: false,
  });
  const rowVirtualizerRef = React.useRef(rowVirtualizer);
  rowVirtualizerRef.current = rowVirtualizer;

  const previousItemsCountRef = React.useRef<number>(0);
  const previousFirstItemKeyRef = React.useRef<string | null>(null);
  const isNearBottomRef = React.useRef<boolean>(true);
  const itemsCountRef = React.useRef<number>(items.length);

  React.useLayoutEffect(() => {
    itemsCountRef.current = items.length;
  }, [items.length]);

  React.useEffect(() => {
    const handle: VirtualizedAgentGroupEventsHandle = {
      getFirstVisibleAnchor: () => {
        const viewport = viewportRef.current;
        if (!viewport) {
          return null;
        }
        const virtualizer = rowVirtualizerRef.current;
        const visibleVirtualItems = virtualizer.getVirtualItems();
        const currentItems = itemsRef.current;
        if (visibleVirtualItems.length === 0 || currentItems.length === 0) {
          return null;
        }
        const scrollOffset = viewport.scrollTop;
        const firstVisible =
          visibleVirtualItems.find((vi) => vi.end > scrollOffset) ??
          visibleVirtualItems[0];
        if (!firstVisible) {
          return null;
        }
        const item = currentItems[firstVisible.index];
        return item ? getDisplayItemAnchor(item) : null;
      },
      restoreToAnchor: (anchor: OlderHistoryAnchor) => {
        requestAnimationFrame(() => {
          const currentItems = itemsRef.current;
          const targetIndex = findAnchorIndex(currentItems, anchor);
          if (targetIndex === -1) {
            return;
          }
          rowVirtualizerRef.current.scrollToIndex(targetIndex, {
            align: "start",
          });
          isNearBottomRef.current = false;
        });
      },
    };
    registerHandle(groupId, handle);
    return () => {
      registerHandle(groupId, null);
    };
  }, [groupId, registerHandle]);

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
    const previousFirstKey = previousFirstItemKeyRef.current;
    const currentFirstKey = items[0]?.key ?? null;
    previousItemsCountRef.current = items.length;
    previousFirstItemKeyRef.current = currentFirstKey;

    if (items.length === 0) {
      return undefined;
    }

    const isInitialMount = previousCount === 0;
    const grew = items.length > previousCount;
    const prepended =
      previousFirstKey !== null &&
      currentFirstKey !== null &&
      previousFirstKey !== currentFirstKey;
    const shouldFollow =
      isInitialMount || (grew && !prepended && isNearBottomRef.current);

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
  }, [items, rowVirtualizer]);

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

export const AgentEventsAccordion = React.forwardRef<
  AgentEventsAccordionHandle,
  AgentEventsAccordionProps
>(function AgentEventsAccordion(
  { events, completedNamespaces },
  ref,
): React.ReactElement {
  const agentGroups = React.useMemo(
    () => groupEventsByAgent(events, completedNamespaces),
    [events, completedNamespaces],
  );
  const [detailItem, setDetailItem] = React.useState<ToolDetailItem | null>(null);
  const [expandedGroups, setExpandedGroups] = React.useState<string[]>([]);

  const validGroupIds = React.useMemo(
    () => new Set(agentGroups.map((group) => group.agentId)),
    [agentGroups],
  );

  const visibleExpandedGroups = React.useMemo(
    () => expandedGroups.filter((groupId) => validGroupIds.has(groupId)),
    [expandedGroups, validGroupIds],
  );

  const handleExpandedGroupsChange = React.useCallback(
    (nextValue: string[]): void => {
      setExpandedGroups(
        nextValue.filter((groupId) => validGroupIds.has(groupId)),
      );
    },
    [validGroupIds],
  );

  const groupHandlesRef = React.useRef<
    Map<string, VirtualizedAgentGroupEventsHandle>
  >(new Map());

  const registerHandle = React.useCallback<RegisterGroupHandle>(
    (groupId, handle) => {
      if (handle) {
        groupHandlesRef.current.set(groupId, handle);
      } else {
        groupHandlesRef.current.delete(groupId);
      }
    },
    [],
  );

  React.useImperativeHandle(
    ref,
    () => ({
      captureOlderHistoryAnchors: () => {
        const anchors: OlderHistoryAnchor[] = [];
        groupHandlesRef.current.forEach((handle, groupId) => {
          const anchor = handle.getFirstVisibleAnchor();
          if (anchor !== null) {
            anchors.push({ groupId, ...anchor });
          }
        });
        return anchors;
      },
      restoreOlderHistoryAnchors: (anchors) => {
        for (const anchor of anchors) {
          const handle = groupHandlesRef.current.get(anchor.groupId);
          if (handle) {
            handle.restoreToAnchor(anchor);
          }
        }
      },
    }),
    [],
  );

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
        value={visibleExpandedGroups}
        onValueChange={handleExpandedGroupsChange}
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
                  groupId={group.agentId}
                  events={group.events}
                  onViewDetails={setDetailItem}
                  registerHandle={registerHandle}
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
});
