import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { getCodebaseAgentRules, type RepositoryAgentSnapshot } from '@/lib/api';
import type {
  AgentType,
  ActivityType,
  CodebaseProgress,
  SSEEvent,
  AggregatedAgentsMdEventData,
  AggregatedSSEEvent,
  AgentMdOutput,
  SSEEventData,
  AgentProgress,
} from '@/types/sse';

const TRACKED_AGENTS: AgentType[] = [
  'project_configuration_agent',
  'development_workflow',
  'business_logic_domain',
];

const TRACKED_AGENT_SET = new Set<AgentType>(TRACKED_AGENTS);

const AGENT_COMPLETION_WEIGHT = (count: number): number => (count / TRACKED_AGENTS.length) * 100;

const countCompletedAgents = (agents: Map<AgentType, AgentProgress>): number => {
  let completed = 0;
  agents.forEach((agent) => {
    if (agent.status === 'completed') {
      completed += 1;
    }
  });
  return completed;
};

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

  // New state for existing snapshot handling
  existingSnapshot: RepositoryAgentSnapshot | null;
  hasExistingSnapshot: boolean;
  isRerunning: boolean;

  connect: (ownerName: string, repoName: string, codebaseIds: string[]) => void;
  disconnect: () => void;
  reset: () => void;
  addEvent: (
    event: SSEEvent,
    parsed: { codebase?: string; agent?: AgentType; activity?: ActivityType | 'status' }
  ) => void;
  initializeFromMetadata: (codebaseIds: string[]) => void;
  setAggregated: (data: AggregatedAgentsMdEventData) => void;

  // New methods for existing snapshot handling
  loadExistingSnapshot: (snapshot: RepositoryAgentSnapshot) => void;
  clearSnapshot: () => void;
  startRerun: () => void;
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

    // Initialize new state for existing snapshot handling
    existingSnapshot: null,
    hasExistingSnapshot: false,
    isRerunning: false,

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
        existingSnapshot: null,
        hasExistingSnapshot: false,
        isRerunning: false,
      }),

    initializeFromMetadata: (codebaseIds: string[]) => {
      set(() => {
        const map = new Map<string, CodebaseProgress>();
        codebaseIds.forEach((id) => {
          const agents = new Map<AgentType, AgentProgress>();
          TRACKED_AGENTS.forEach((agent) => {
            agents.set(agent, {
              agentType: agent,
              status: 'idle',
              events: [] as SSEEventData[],
              progress: 0,
            });
          });

          map.set(id, {
            codebaseId: id,
            codebaseName: id,
            agents,
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
              agents: (() => {
                const agents = new Map<AgentType, AgentProgress>();
                TRACKED_AGENTS.forEach((agent) => {
                  agents.set(agent, {
                    agentType: agent,
                    status: 'idle',
                    events: [] as SSEEventData[],
                    progress: 0,
                  });
                });
                return agents;
              })(),
              overallProgress: 0,
              status: 'initializing',
              events: [],
              startTime: new Date(),
            };

          cb.events.push(event);

          const activity = parsed.activity;

          if (activity === 'complete' && parsed.agent && TRACKED_AGENT_SET.has(parsed.agent)) {
            const agent = cb.agents.get(parsed.agent) ?? {
              agentType: parsed.agent,
              status: 'idle',
              events: [] as SSEEventData[],
              progress: 0,
            };

            agent.status = 'completed';
            agent.progress = 100;
            agent.lastActivity = 'complete';
            agent.lastUpdate = new Date();
            agent.events.push(event.data as SSEEventData);
            cb.agents.set(parsed.agent, agent);

            const completedAgents = countCompletedAgents(cb.agents);
            const progress = AGENT_COMPLETION_WEIGHT(completedAgents);
            cb.overallProgress = Math.min(100, Number(progress.toFixed(2)));
            cb.status = completedAgents === TRACKED_AGENTS.length ? 'completed' : 'processing';
          } else if (activity === 'status' && (event.data as unknown as { message?: string })?.message?.toLowerCase()?.includes('complete')) {
            cb.overallProgress = 100;
            cb.status = 'completed';
          } else if (activity && activity !== 'status') {
            cb.status = 'processing';
          }

          codebases.set(parsed.codebase, cb);

          const arr = Array.from(codebases.values());
          const totalCompletedAgents = arr.reduce((sum, c) => sum + countCompletedAgents(c.agents), 0);
          const expectedCompleteEvents = arr.length * TRACKED_AGENTS.length;
          const overall = expectedCompleteEvents
            ? Math.min(100, Number(((totalCompletedAgents / expectedCompleteEvents) * 100).toFixed(2)))
            : 0;
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

    loadExistingSnapshot: (snapshot) => {
      // Parse stringified JSON for each codebase from the snapshot
      const parsedCodebases: Record<string, AgentMdOutput> = {};

      for (const [codebaseName, jsonString] of Object.entries(snapshot.codebases)) {
        try {
          parsedCodebases[codebaseName] = JSON.parse(jsonString) as AgentMdOutput;
        } catch (error) {
          console.error(`Failed to parse JSON for codebase ${codebaseName}:`, error);
        }
      }

      set({
        existingSnapshot: snapshot,
        hasExistingSnapshot: true,
        parsedCodebases,
        isComplete: true,
        overallProgress: 100,
        isRerunning: false,
      });
    },

    clearSnapshot: () => {
      set({
        existingSnapshot: null,
        hasExistingSnapshot: false,
        parsedCodebases: null,
        isComplete: false,
        overallProgress: 0,
        isRerunning: false,
      });
    },

    startRerun: () => {
      set({
        existingSnapshot: null,
        hasExistingSnapshot: false,
        parsedCodebases: null,
        isComplete: false,
        overallProgress: 0,
        isRerunning: true,
        events: [],
        codebases: new Map(),
        error: null,
      });
    },
  }))
);
