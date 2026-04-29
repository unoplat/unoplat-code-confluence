/* eslint-disable react/jsx-no-bind */
import React from "react";
import { ArrowDown, Loader2 } from "lucide-react";

import {
  AgentEventsAccordion,
  type AgentEventsAccordionHandle,
  type OlderHistoryAnchor,
} from "@/components/custom/agent-events";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { RepositoryAgentSnapshotScope } from "@/features/repository-agent-snapshots/collection";
import { useRepositoryAgentEventHistory } from "@/features/repository-agent-snapshots/hooks";
import {
  getAgentGroupSummaryCounts,
  groupEventsByAgent,
} from "@/lib/agent-events-utils";
import type { RepositoryAgentCodebaseProgressRow } from "@/features/repository-agent-snapshots/schema";
import type { ParsedRepositoryAgentSnapshot } from "@/features/repository-agent-snapshots/transformers";

const bottomFollowThreshold = 48;

interface EventBounds {
  newestEventId: number | null;
  oldestEventId: number | null;
}

interface LoadedBoundsChange {
  olderHistoryPrepended: boolean;
  latestEventAppended: boolean;
}

interface GenerateAgentsProgressLiveProps {
  snapshot: ParsedRepositoryAgentSnapshot | null;
  scope: RepositoryAgentSnapshotScope;
  progressRows: RepositoryAgentCodebaseProgressRow[];
  isSyncing: boolean;
}

function getCodebaseDisplayName(codebaseName: string): string {
  return codebaseName === "." ? "Root" : codebaseName;
}

function getAverageProgress(
  progressRows: RepositoryAgentCodebaseProgressRow[],
): number {
  if (progressRows.length === 0) {
    return 0;
  }

  const total = progressRows.reduce(
    (sum, row) => sum + (typeof row.progress === "number" ? row.progress : 0),
    0,
  );
  return total / progressRows.length;
}

function getLoadedEventBounds(eventIds: number[]): EventBounds {
  if (eventIds.length === 0) {
    return {
      newestEventId: null,
      oldestEventId: null,
    };
  }

  return {
    newestEventId: eventIds[eventIds.length - 1] ?? null,
    oldestEventId: eventIds[0] ?? null,
  };
}

function getLoadedBoundsChange(
  previousBounds: EventBounds,
  nextBounds: EventBounds,
): LoadedBoundsChange {
  return {
    olderHistoryPrepended:
      previousBounds.oldestEventId !== null &&
      nextBounds.oldestEventId !== null &&
      nextBounds.oldestEventId < previousBounds.oldestEventId,
    latestEventAppended:
      previousBounds.newestEventId !== null &&
      nextBounds.newestEventId !== null &&
      nextBounds.newestEventId > previousBounds.newestEventId,
  };
}

function isViewportNearBottom(viewport: HTMLDivElement): boolean {
  return (
    viewport.scrollHeight - viewport.scrollTop - viewport.clientHeight <=
    bottomFollowThreshold
  );
}

function scrollViewportToBottom(viewport: HTMLDivElement | null): void {
  if (!viewport) {
    return;
  }

  viewport.scrollTo({
    top: viewport.scrollHeight,
    behavior: "auto",
  });
}

function getActiveCodebaseName(
  activeCodebaseName: string,
  codebaseNames: string[],
): string {
  if (codebaseNames.length === 0) {
    return "";
  }

  if (codebaseNames.includes(activeCodebaseName)) {
    return activeCodebaseName;
  }

  return codebaseNames[0] ?? "";
}

function getWaitingMessage(
  isSyncing: boolean,
  isHistoryLoading: boolean,
): string {
  if (isHistoryLoading || isSyncing) {
    return "Waiting for ElectricSQL updates…";
  }

  return "No events available yet.";
}

function getCodebaseAgentSummary(
  events: ReturnType<typeof groupEventsByAgent>,
): string | null {
  const summary = getAgentGroupSummaryCounts(events);
  const parts: string[] = [];

  if (summary.completed > 0) {
    parts.push(`${summary.completed} completed`);
  }

  if (summary.running > 0) {
    parts.push(`${summary.running} running`);
  }

  if (summary.pending > 0) {
    parts.push(`${summary.pending} pending`);
  }

  return parts.length > 0 ? parts.join(" · ") : null;
}

export function GenerateAgentsProgressLive({
  snapshot,
  scope,
  progressRows,
  isSyncing,
}: GenerateAgentsProgressLiveProps): React.ReactElement {
  const codebaseNames = progressRows.map((row) => row.codebase_name);
  const [activeCodebaseName, setActiveCodebaseName] = React.useState<string>(
    codebaseNames[0] ?? "",
  );
  const resolvedActiveCodebaseName = getActiveCodebaseName(
    activeCodebaseName,
    codebaseNames,
  );
  const [previousResolvedCodebaseName, setPreviousResolvedCodebaseName] =
    React.useState<string>(resolvedActiveCodebaseName);
  const viewportRef = React.useRef<HTMLDivElement | null>(null);
  const accordionRef = React.useRef<AgentEventsAccordionHandle | null>(null);
  const pendingOlderHistoryAnchorsRef = React.useRef<
    OlderHistoryAnchor[] | null
  >(null);
  const isNearBottomRef = React.useRef<boolean>(true);
  const shouldSnapToBottomRef = React.useRef<boolean>(true);
  const previousLoadedBoundsRef = React.useRef<EventBounds>({
    newestEventId: null,
    oldestEventId: null,
  });
  const [hasUnseenLatest, setHasUnseenLatest] = React.useState<boolean>(false);

  if (previousResolvedCodebaseName !== resolvedActiveCodebaseName) {
    setPreviousResolvedCodebaseName(resolvedActiveCodebaseName);
    setHasUnseenLatest(false);
  }

  const activeProgressRow =
    progressRows.find(
      (row) => row.codebase_name === resolvedActiveCodebaseName,
    ) ?? progressRows[0];
  const {
    events,
    hasOlderHistory,
    isFetchingOlderHistory,
    isLoading: isHistoryLoading,
    isError: isHistoryError,
    loadOlderHistory,
  } = useRepositoryAgentEventHistory(scope, resolvedActiveCodebaseName);
  const progress = activeProgressRow?.progress ?? 0;
  const overallProgress =
    snapshot?.overallProgress ?? getAverageProgress(progressRows);
  const loadedBounds = React.useMemo(
    () => getLoadedEventBounds(events.map((event) => event.event_id)),
    [events],
  );
  const completedNamespaces = activeProgressRow?.completed_namespaces ?? [];
  const agentGroups = groupEventsByAgent(events, completedNamespaces);
  const codebaseAgentSummary = getCodebaseAgentSummary(agentGroups);
  const waitingForEvents = events.length === 0;
  const isSingleRootCodebase =
    codebaseNames.length === 1 && codebaseNames[0] === ".";

  React.useLayoutEffect(() => {
    shouldSnapToBottomRef.current = true;
    isNearBottomRef.current = true;
    pendingOlderHistoryAnchorsRef.current = null;
    previousLoadedBoundsRef.current = {
      newestEventId: null,
      oldestEventId: null,
    };
  }, [resolvedActiveCodebaseName]);

  React.useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) {
      return undefined;
    }

    const currentViewport = viewport;

    function handleViewportScroll(): void {
      const isNearBottom = isViewportNearBottom(currentViewport);
      isNearBottomRef.current = isNearBottom;

      if (isNearBottom) {
        setHasUnseenLatest(false);
      }
    }

    handleViewportScroll();
    currentViewport.addEventListener("scroll", handleViewportScroll, {
      passive: true,
    });

    return () => {
      currentViewport.removeEventListener("scroll", handleViewportScroll);
    };
  }, [resolvedActiveCodebaseName]);

  React.useLayoutEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) {
      previousLoadedBoundsRef.current = loadedBounds;
      return;
    }

    const previousLoadedBounds = previousLoadedBoundsRef.current;
    const boundsChange = getLoadedBoundsChange(
      previousLoadedBounds,
      loadedBounds,
    );

    if (
      pendingOlderHistoryAnchorsRef.current &&
      boundsChange.olderHistoryPrepended &&
      !isFetchingOlderHistory
    ) {
      const anchors = pendingOlderHistoryAnchorsRef.current;
      pendingOlderHistoryAnchorsRef.current = null;
      accordionRef.current?.restoreOlderHistoryAnchors(anchors);
    }

    let nextHasUnseenLatest: boolean | null = null;

    if (shouldSnapToBottomRef.current) {
      scrollViewportToBottom(viewport);
      shouldSnapToBottomRef.current = false;
      isNearBottomRef.current = true;
      nextHasUnseenLatest = false;
    } else if (boundsChange.latestEventAppended) {
      if (isNearBottomRef.current || isViewportNearBottom(viewport)) {
        scrollViewportToBottom(viewport);
        isNearBottomRef.current = true;
        nextHasUnseenLatest = false;
      } else {
        nextHasUnseenLatest = true;
      }
    }

    previousLoadedBoundsRef.current = loadedBounds;

    if (nextHasUnseenLatest !== null) {
      setHasUnseenLatest(nextHasUnseenLatest);
    }
  }, [isFetchingOlderHistory, loadedBounds]);

  function handleCodebaseChange(nextCodebaseName: string): void {
    setActiveCodebaseName(nextCodebaseName);
  }

  function handleLoadOlderHistory(): void {
    const anchors = accordionRef.current?.captureOlderHistoryAnchors() ?? [];
    pendingOlderHistoryAnchorsRef.current = anchors;
    loadOlderHistory();
  }

  function handleJumpToLatest(): void {
    scrollViewportToBottom(viewportRef.current);
    setHasUnseenLatest(false);
  }

  return (
    <div className="flex h-full flex-col gap-4">
      <Card className="mb-3 p-4">
        <div className="space-y-3">
          <div className="flex items-center justify-center gap-3">
            <div className="text-foreground text-sm">Repository Progress</div>
            <div className="text-primary text-sm font-medium">
              {Math.round(overallProgress)}%
            </div>
          </div>
          <Progress value={overallProgress} />
        </div>
      </Card>

      <Card className="flex min-h-0 flex-1 flex-col p-4">
        <div className="space-y-3">
          <div className="flex items-center justify-center gap-3">
            {!isSingleRootCodebase ? (
              <Select
                value={resolvedActiveCodebaseName}
                onValueChange={handleCodebaseChange}
              >
                <SelectTrigger className="bg-muted/50 hover:bg-muted/80 max-w-80 cursor-pointer transition-colors">
                  <SelectValue placeholder="Select codebase" />
                </SelectTrigger>
                <SelectContent>
                  {codebaseNames.map((codebaseName) => (
                    <SelectItem key={codebaseName} value={codebaseName}>
                      {getCodebaseDisplayName(codebaseName)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <div className="text-foreground text-sm font-medium">
                {getCodebaseDisplayName(resolvedActiveCodebaseName)}
              </div>
            )}
            <div className="text-primary text-sm font-medium">
              {Math.round(progress)}%
            </div>
          </div>

          <Progress value={progress} />

          {codebaseAgentSummary ? (
            <div className="text-muted-foreground text-xs">
              {codebaseAgentSummary}
            </div>
          ) : null}

          <div className="border-border relative min-h-0 flex-1 overflow-hidden rounded-md border">
            <ScrollArea className="h-80 w-full" viewportRef={viewportRef}>
              {hasOlderHistory && events.length > 0 ? (
                <div className="flex justify-center px-3 py-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={isFetchingOlderHistory}
                    onClick={handleLoadOlderHistory}
                  >
                    {isFetchingOlderHistory ? (
                      <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                    ) : null}
                    Load older events
                  </Button>
                </div>
              ) : null}

              {isHistoryError ? (
                <p className="text-destructive px-3 py-3 text-sm">
                  Failed to sync event history for this codebase.
                </p>
              ) : waitingForEvents ? (
                <p className="text-muted-foreground px-3 py-3 text-sm">
                  {getWaitingMessage(isSyncing, isHistoryLoading)}
                </p>
              ) : (
                <AgentEventsAccordion
                  ref={accordionRef}
                  events={events}
                  completedNamespaces={completedNamespaces}
                />
              )}
            </ScrollArea>

            {hasUnseenLatest ? (
              <div className="pointer-events-none absolute inset-x-0 bottom-2 flex justify-center">
                <Button
                  variant="secondary"
                  size="sm"
                  className="pointer-events-auto shadow-md"
                  onClick={handleJumpToLatest}
                >
                  <ArrowDown className="mr-1.5 h-3.5 w-3.5" />
                  New events
                </Button>
              </div>
            ) : null}
          </div>
        </div>
      </Card>
    </div>
  );
}
