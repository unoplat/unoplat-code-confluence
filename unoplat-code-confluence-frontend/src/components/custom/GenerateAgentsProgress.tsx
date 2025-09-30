import React from 'react';
import type { IngestedRepository } from '@/types';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { ParsedRepositoryAgentSnapshot, RepositoryAgentCodebaseState } from '@/features/repository-agent-snapshots/transformers';

interface GenerateAgentsProgressProps {
  repository: IngestedRepository;
  snapshot: ParsedRepositoryAgentSnapshot | null;
  codebaseIds: string[];
  isSyncing: boolean;
}

export function GenerateAgentsProgress({ repository, snapshot, codebaseIds, isSyncing }: GenerateAgentsProgressProps): React.ReactElement {
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

  const [active, setActive] = React.useState<string>(codebaseNames[0] ?? '');
  const viewportRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (codebaseNames.length === 0) {
      setActive('');
      return;
    }

    if (!codebaseNames.includes(active)) {
      setActive(codebaseNames[0]);
    }
  }, [codebaseNames, active]);

  const activeState = derivedCodebases.find((entry) => entry.codebaseName === active) ?? derivedCodebases[0];
  const progress = typeof activeState?.progress === 'number' ? activeState.progress : 0;
  const events = activeState?.events ?? [];

  React.useEffect(() => {
    const scrollToBottom = () => {
      if (viewportRef.current) {
        viewportRef.current.scrollTo({
          top: viewportRef.current.scrollHeight,
          behavior: 'smooth'
        });
      }
    };

    // Small delay to ensure DOM is updated
    const timeoutId = setTimeout(scrollToBottom, 50);

    return () => clearTimeout(timeoutId);
  }, [events.length, active]);

  const overallProgress = snapshot?.overallProgress ?? 0;
  const waitingForEvents = events.length === 0;
  const isSingleRootCodebase = codebaseNames.length === 1 && codebaseNames[0] === '.';

  const getDisplayName = (name: string) => name === '.' ? 'Root' : name;

  return (
    <div className="flex flex-col gap-4 h-full">
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Overall</div>
            <div className="text-sm font-medium">
            {repository.repository_owner_name}/{repository.repository_name}
            </div>
          </div>
          <div className="w-1/2">
            <Progress value={overallProgress} />
          </div>
        </div>
      </Card>

      <Card className="p-4 flex-1 min-h-0 flex flex-col">
        {!isSingleRootCodebase && (
          <div className="flex items-center justify-center mb-4">
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
        <div className="flex flex-col gap-3 flex-1 min-h-0">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium">{getDisplayName(active)}</div>
            <div className="w-1/2">
              <Progress value={progress} />
            </div>
          </div>
          <ScrollArea className="h-64 w-full border rounded-md" viewportRef={viewportRef}>
            <div className="p-3 space-y-2 overflow-x-hidden">
              {waitingForEvents && (
                <div className="text-sm text-muted-foreground">
                  {isSyncing ? 'Waiting for ElectricSQL updates…' : 'No events available yet.'}
                </div>
              )}
              {events.map((event) => (
                <div key={`${event.id}-${event.event}`} className="text-xs whitespace-pre-wrap break-all max-w-full">
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
