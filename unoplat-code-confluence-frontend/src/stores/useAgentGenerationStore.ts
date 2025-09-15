import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { getCodebaseAgentRules } from '@/lib/api';
import type { AgentType, ActivityType, CodebaseProgress, SSEEvent, AggregatedAgentsMdEventData, AggregatedSSEEvent, AgentMdOutput } from '@/types/sse';

interface AgentGenerationState {
  connection: EventSource | null;
  isConnected: boolean;
  error: string | null;

  ownerName: string | null;
  repoName: string | null;
  codebaseIds: string[];

  events: SSEEvent[];
  codebases: Map<string, CodebaseProgress>;
  overallProgress: number;
  isComplete: boolean;
  aggregated: AggregatedAgentsMdEventData | null;
  parsedCodebases: Record<string, AgentMdOutput> | null;

  connect: (ownerName: string, repoName: string, codebaseIds: string[]) => void;
  disconnect: () => void;
  reset: () => void;
  addEvent: (
    event: SSEEvent,
    parsed: { codebase?: string; agent?: AgentType; activity?: ActivityType | 'status' }
  ) => void;
  initializeFromMetadata: (codebaseIds: string[]) => void;
  setAggregated: (data: AggregatedAgentsMdEventData) => void;
}

export const useAgentGenerationStore = create<AgentGenerationState>()(
  subscribeWithSelector((set, get) => ({
    connection: null,
    isConnected: false,
    error: null,

    ownerName: null,
    repoName: null,
    codebaseIds: [],

    events: [],
    codebases: new Map<string, CodebaseProgress>(),
    overallProgress: 0,
    isComplete: false,
    aggregated: null,
    parsedCodebases: null,

    connect: (ownerName: string, repoName: string, codebaseIds: string[]) => {
      const { disconnect, addEvent, initializeFromMetadata, setAggregated } = get();
      disconnect();
      initializeFromMetadata(codebaseIds);

      const es = getCodebaseAgentRules({
        ownerName,
        repoName,
        codebaseIds,
        onEvent: (event, parsed) => addEvent(event, parsed),
        onAggregated: (aggEvent: AggregatedSSEEvent) => {
          setAggregated(aggEvent.data);
        },
        onError: (e) => set({ error: e.message }),
      });

      set({ connection: es, isConnected: true, error: null, ownerName, repoName, codebaseIds });
    },

    disconnect: () => {
      const { connection } = get();
      if (connection) {
        connection.close();
      }
      set({ connection: null, isConnected: false });
    },

    reset: () =>
      set({
        events: [],
        codebases: new Map<string, CodebaseProgress>(),
        overallProgress: 0,
        isComplete: false,
        aggregated: null,
        parsedCodebases: null,
        error: null,
      }),

    initializeFromMetadata: (codebaseIds: string[]) => {
      set(() => {
        const map = new Map<string, CodebaseProgress>();
        codebaseIds.forEach((id) => {
          map.set(id, {
            codebaseId: id,
            codebaseName: id,
            agents: new Map(),
            overallProgress: 0,
            status: 'initializing',
            events: [],
            startTime: new Date(),
          });
        });
        return { codebases: map };
      });
    },

    addEvent: (event, parsed) => {
      set((state) => {
        const trimmed = state.events.length > 1000 ? state.events.slice(-800) : state.events;
        const events = [...trimmed, event];

        if (parsed.codebase) {
          const codebases = new Map(state.codebases);
          const existing = codebases.get(parsed.codebase);
          const cb: CodebaseProgress =
            existing || {
              codebaseId: parsed.codebase,
              codebaseName: parsed.codebase,
              agents: new Map(),
              overallProgress: 0,
              status: 'initializing',
              events: [],
              startTime: new Date(),
            };

          cb.events.push(event);

          const activity = parsed.activity;
          if (activity === 'tool.result' || activity === 'result' || activity === 'complete') {
            cb.overallProgress = Math.min(100, cb.overallProgress + 3);
          } else if (activity === 'status' && (event.data as unknown as { message?: string })?.message?.toLowerCase()?.includes('complete')) {
            cb.overallProgress = 100;
            cb.status = 'completed';
          } else {
            cb.status = 'processing';
          }

          codebases.set(parsed.codebase, cb);

          const arr = Array.from(codebases.values());
          const total = arr.reduce((sum, c) => sum + (c.overallProgress || 0), 0);
          const overall = arr.length ? Math.floor(total / arr.length) : 0;
          return { codebases, events, overallProgress: overall };
        }

        return { events };
      });
    },

    setAggregated: (data) => {
      // Parse stringified JSON for each codebase
      const parsedCodebases: Record<string, AgentMdOutput> = {};

      for (const [codebaseName, jsonString] of Object.entries(data.codebases)) {
        try {
          parsedCodebases[codebaseName] = JSON.parse(jsonString) as AgentMdOutput;
        } catch (error) {
          console.error(`Failed to parse JSON for codebase ${codebaseName}:`, error);
        }
      }

      set(() => ({
        aggregated: data,
        parsedCodebases,
        isComplete: true,
        overallProgress: 100,
      }));
    },
  }))
);


