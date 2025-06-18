import { useCallback, useMemo, useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useSseStreamedQuery } from './useSseStreamedQuery';
import { env } from '@/lib/env';
import type {
  DetectionProgress,
  DetectionResult,
  DetectionError,
  CodebaseConfig,
} from '@/types';
import type { Codebase } from '@/components/custom/CodebaseForm';

export type DetectionStatus = 'idle' | 'detecting' | 'success' | 'error';

export interface UseDetectCodebasesOptions {
  /** Git URL to stream detection for. If falsy, no request is made. */
  gitUrl?: string | null;
  onSuccess?: (result: DetectionResult) => void;
  onError?: (error: DetectionError) => void;
}

export interface UseDetectCodebasesReturn {
  status: DetectionStatus;
  error: string | null;
  codebases: Codebase[];
  cancelDetection: () => void;
}

// Stream chunk union – distinguishes event type coming from backend
export type DetectionStreamChunk =
  | { event: 'progress'; data: DetectionProgress }
  | { event: 'result'; data: DetectionResult }
  | { event: 'error'; data: DetectionError }
  | { event: 'done'; data: DetectionResult };

function mapResultToCodebases(result: DetectionResult): Codebase[] {
  return result.codebases.map((config: CodebaseConfig) => ({
    codebase_folder: config.codebase_folder,
    root_packages: config.root_packages || null,
    programming_language_metadata: {
      language: config.programming_language_metadata.language,
      package_manager: config.programming_language_metadata.package_manager || 'uv',
      language_version: config.programming_language_metadata.language_version || undefined,
      role: config.programming_language_metadata.role,
      manifest_path: config.programming_language_metadata.manifest_path || undefined,
      project_name: config.programming_language_metadata.project_name || undefined,
    },
  }));
}

export function useDetectCodebases({ gitUrl, onSuccess, onError }: UseDetectCodebasesOptions = {}): UseDetectCodebasesReturn {
  const queryClient = useQueryClient();

  // --- Streaming query ---------------------------------------------------
  const {
    data: chunks = [],
    fetchStatus,
  } = useSseStreamedQuery<DetectionStreamChunk>(
    ['detect-codebases', gitUrl],
    gitUrl ? `${env.apiBaseUrl}/detect-codebases-sse?git_url=${encodeURIComponent(gitUrl)}` : '',
    {
      enabled: !!gitUrl,
      eventNames: ['connected', 'progress', 'result', 'error', 'done'],
      // keep only last 200 chunks to avoid memory blow-up (tweak as needed)
      maxChunks: 200,
    },
  );

  // Debug: log chunks as they arrive during development
  useEffect(() => {
    if (chunks.length > 0) {
      // log only the last chunk to avoid flooding
      const c = chunks[chunks.length - 1];
       
      console.debug('[useDetectCodebases] chunk', c);
    }
  }, [chunks]);

  // --- Derive state ------------------------------------------------------
  const firstResultChunk = useMemo(() =>
    chunks.find((c): c is { event: 'result'; data: DetectionResult } => c?.event === 'result'),
  [chunks]);

  const firstErrorChunk = useMemo(() =>
    chunks.find((c): c is { event: 'error'; data: DetectionError } => c?.event === 'error'),
  [chunks]);

  // Some backends may send the final payload with event:"done" instead of
  // "result". If so, treat it as a valid result as long as it contains a
  // `codebases` array.
  const firstDoneChunkWithCodebases = useMemo(() =>
    chunks.find(
      (c): c is { event: 'done'; data: DetectionResult } =>
        c?.event === 'done' && c.data && typeof c.data === 'object' && 'codebases' in c.data),
  [chunks]);

  const status: DetectionStatus = useMemo(() => {
    if (!gitUrl) return 'idle';
    if (firstErrorChunk) return 'error';
    if (firstResultChunk || firstDoneChunkWithCodebases) return 'success';
    if (fetchStatus === 'fetching') return 'detecting';
    return 'idle';
  }, [gitUrl, firstErrorChunk, firstResultChunk, firstDoneChunkWithCodebases, fetchStatus]);

  const error = useMemo(() => {
    if (firstErrorChunk && firstErrorChunk.data && typeof firstErrorChunk.data === 'object') {
      return (firstErrorChunk.data as DetectionError).error ?? 'Unknown error';
    }
    return null;
  }, [firstErrorChunk]);

  const codebases = useMemo((): Codebase[] => {
    if (firstResultChunk) {
      return mapResultToCodebases(firstResultChunk.data);
    }
    if (firstDoneChunkWithCodebases) {
      return mapResultToCodebases(firstDoneChunkWithCodebases.data);
    }
    return [];
  }, [firstResultChunk, firstDoneChunkWithCodebases]);

  // Fire completion / error callbacks only once when the corresponding
  // chunks arrive. We keep track of whether we've already invoked the
  // callbacks using refs to avoid repeated calls on re-renders.
  const hasFiredSuccessRef = useRef(false);
  const hasFiredErrorRef = useRef(false);

  useEffect(() => {
    const resultToFire = firstResultChunk || firstDoneChunkWithCodebases;
    if (resultToFire && !hasFiredSuccessRef.current) {
      hasFiredSuccessRef.current = true;
      onSuccess?.(resultToFire.data);
    }

    if (firstErrorChunk && !hasFiredErrorRef.current) {
      hasFiredErrorRef.current = true;
      onError?.(firstErrorChunk.data);
    }
  }, [firstResultChunk, firstDoneChunkWithCodebases, firstErrorChunk, onSuccess, onError]);

  // --- Control functions -------------------------------------------------
  const cancelDetection = useCallback(() => {
    if (gitUrl) {
      queryClient.cancelQueries({ queryKey: ['detect-codebases', gitUrl] });
    }
  }, [gitUrl, queryClient]);

  return {
    status,
    error,
    codebases,
    cancelDetection,
  };
} 