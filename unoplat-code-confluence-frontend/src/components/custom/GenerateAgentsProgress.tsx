import React from "react";
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
import type {
  ParsedRepositoryAgentSnapshot,
  RepositoryAgentCodebaseState,
} from "@/features/repository-agent-snapshots/transformers";

interface GenerateAgentsProgressProps {
  repositoryOwnerName: string;
  repositoryName: string;
  runId: string;
  snapshot: ParsedRepositoryAgentSnapshot | null;
  codebaseIds: string[];
  isSyncing: boolean;
}

export function GenerateAgentsProgress({
  repositoryOwnerName,
  repositoryName,
  runId,
  snapshot,
  codebaseIds,
  isSyncing,
}: GenerateAgentsProgressProps): React.ReactElement {
  const derivedCodebases: RepositoryAgentCodebaseState[] = React.useMemo(() => {
    if (snapshot?.codebases && snapshot.codebases.length > 0) {
      return snapshot.codebases;
    }

    return codebaseIds.map((codebaseName) => ({
      codebaseName,
      progress: null,
      events: [],
    }));
  }, [snapshot?.codebases, codebaseIds]);

  const codebaseNames = derivedCodebases.map((entry) => entry.codebaseName);

  const [active, setActive] = React.useState<string>(codebaseNames[0] ?? "");
  const viewportRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (codebaseNames.length === 0) {
      setActive("");
      return;
    }

    if (!codebaseNames.includes(active)) {
      setActive(codebaseNames[0]);
    }
  }, [codebaseNames, active]);

  const activeState =
    derivedCodebases.find((entry) => entry.codebaseName === active) ??
    derivedCodebases[0];
  const progress =
    typeof activeState?.progress === "number" ? activeState.progress : 0;
  const events = activeState?.events ?? [];

  React.useEffect(() => {
    const scrollToBottom = () => {
      if (viewportRef.current) {
        viewportRef.current.scrollTo({
          top: viewportRef.current.scrollHeight,
          behavior: "smooth",
        });
      }
    };

    // Small delay to ensure DOM is updated
    const timeoutId = setTimeout(scrollToBottom, 50);

    return () => clearTimeout(timeoutId);
  }, [events.length, active]);

  const overallProgress = snapshot?.overallProgress ?? 0;
  const waitingForEvents = events.length === 0;
  const isSingleRootCodebase =
    codebaseNames.length === 1 && codebaseNames[0] === ".";

  const getDisplayName = (name: string) => (name === "." ? "Root" : name);

  return (
    <div className="flex h-full flex-col gap-4">
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="text-muted-foreground text-sm">Overall</div>
            <div className="text-sm font-medium">
              {repositoryOwnerName}/{repositoryName}
            </div>
            <div
              className="text-muted-foreground truncate font-mono text-xs"
              title={runId}
            >
              Run: {runId}
            </div>
          </div>
          <div className="w-1/2">
            <Progress value={overallProgress} />
          </div>
        </div>
      </Card>

      <Card className="flex min-h-0 flex-1 flex-col p-4">
        {!isSingleRootCodebase && (
          <div className="mb-4 flex items-center justify-center">
            <Select value={active} onValueChange={setActive}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Select codebase" />
              </SelectTrigger>
              <SelectContent>
                {codebaseNames.map((name) => (
                  <SelectItem key={name} value={name}>
                    {getDisplayName(name)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
        <div className="flex min-h-0 flex-1 flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium">{getDisplayName(active)}</div>
            <div className="w-1/2">
              <Progress value={progress} />
            </div>
          </div>
          <ScrollArea
            className="border-border h-64 w-full rounded-md border"
            viewportRef={viewportRef}
          >
            <div className="space-y-2 overflow-x-hidden p-3">
              {waitingForEvents && (
                <div className="text-muted-foreground text-sm">
                  {isSyncing
                    ? "Waiting for ElectricSQL updates…"
                    : "No events available yet."}
                </div>
              )}
              {events.map((event) => (
                <div
                  key={`${event.id}-${event.event}`}
                  className="max-w-full text-xs break-all whitespace-pre-wrap"
                >
                  {event.message ?? event.event}
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </Card>
    </div>
  );
}
