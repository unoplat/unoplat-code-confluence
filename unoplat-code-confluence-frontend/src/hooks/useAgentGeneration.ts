import { useEffect } from 'react';
import type { IngestedRepository } from '@/types';
import { useAgentGenerationStore } from '@/stores/useAgentGenerationStore';

interface UseAgentGenerationOptions {
  repository: IngestedRepository;
  codebaseIds: string[];
  autoConnect?: boolean;
}

export function useAgentGeneration({ repository, codebaseIds, autoConnect = false }: UseAgentGenerationOptions) {
  const { connect, disconnect, isConnected, error } = useAgentGenerationStore();

  useEffect(() => {
    if (autoConnect && repository) {
      connect(repository.repository_owner_name, repository.repository_name, codebaseIds);
    }
    return () => {
      if (autoConnect) {
        disconnect();
      }
    };
  }, [repository, codebaseIds, autoConnect, connect, disconnect]);

  return {
    isConnected,
    error,
    connect: () => connect(repository.repository_owner_name, repository.repository_name, codebaseIds),
    disconnect,
  } as const;
}


