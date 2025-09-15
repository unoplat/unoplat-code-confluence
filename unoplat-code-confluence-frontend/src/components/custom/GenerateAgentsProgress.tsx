import React from 'react';
import type { IngestedRepository } from '@/types';
import { useAgentGenerationStore } from '@/stores/useAgentGenerationStore';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { SSEEventData } from '@/types/sse';

interface GenerateAgentsProgressProps {
  repository: IngestedRepository;
  codebaseIds: string[];
}

export function GenerateAgentsProgress({ repository, codebaseIds }: GenerateAgentsProgressProps): React.ReactElement {
  const codebases = useAgentGenerationStore((s) => s.codebases);
  const overallProgress = useAgentGenerationStore((s) => s.overallProgress);
  const [active, setActive] = React.useState<string>(codebaseIds[0] ?? '');

  React.useEffect(() => {
    if (!codebaseIds.includes(active) && codebaseIds.length > 0) {
      setActive(codebaseIds[0]);
    }
  }, [codebaseIds, active]);

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
        <div className="flex items-center justify-center mb-4">
          <Select value={active} onValueChange={setActive}>
            <SelectTrigger className="w-64">
              <SelectValue placeholder="Select codebase" />
            </SelectTrigger>
            <SelectContent>
              {codebaseIds.map((id) => (
                <SelectItem key={id} value={id}>
                  {id}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {(() => {
          const cb = codebases.get(active);
          const progress = cb?.overallProgress ?? 0;
          const events = cb?.events ?? [];
          
          return (
            <div className="flex flex-col gap-3 flex-1 min-h-0">
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium">{active}</div>
                <div className="w-1/2">
                  <Progress value={progress} />
                </div>
              </div>
              <ScrollArea className="h-64 w-full border rounded-md">
                <div className="p-3 space-y-2">
                  {events.length === 0 && (
                    <div className="text-sm text-muted-foreground">Waiting for events…</div>
                  )}
                  {events.map((e, idx) => (
                    <div key={idx} className="text-xs break-words whitespace-pre-wrap">
                      {isSSEEventData(e.data) ? e.data.message : JSON.stringify(e.data)}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          );
        })()}
      </Card>
    </div>
  );
}

function isSSEEventData(data: unknown): data is SSEEventData {
  if (typeof data !== 'object' || data === null) {
    return false;
  }
  return 'message' in (data as Record<string, unknown>);
}


