import { QueryKey, QueryFunctionContext, UseQueryResult, useQuery, experimental_streamedQuery as streamedQuery } from '@tanstack/react-query';

/**
 * Options for `useSseStreamedQuery`.
 */
export interface UseSseStreamedQueryOptions<TChunk> {
  /**
   * Whether the query is enabled. Defaults to `true`.
   */
  enabled?: boolean;
  /**
   * How refetches should be handled. Mirrors `refetchMode` option of `streamedQuery`.
   * – `reset`  ➜ clear accumulated data and start over (default)
   * – `append` ➜ keep existing data and append new chunks
   * – `replace` ➜ replace all data once the stream finishes
   */
  refetchMode?: 'append' | 'reset' | 'replace';
  /**
   * Maximum number of chunks to retain in React Query cache. If `undefined`, all
   * chunks are kept (beware of unbounded memory growth for long-running streams).
   */
  maxChunks?: number;
  /**
   * Optional initial data used before the first chunk arrives.
   */
  initialData?: TChunk[];
  /**
   * Array of EventSource event names to listen to. Defaults to ['message'].
   */
  eventNames?: string[];
}

/**
 * Convert an EventSource stream into an **`AsyncIterable`** so it can be
 * consumed by TanStack Query's `streamedQuery` helper.
 *
 * The generator yields a parsed JSON payload for each incoming **`message`**
 * event. If JSON parsing fails it will yield the raw string.
 */
function eventSourceToAsyncIterable<T>(url: string, signal?: AbortSignal, eventNames: string[] = ['message']): AsyncIterable<T> {
  return {
    async *[Symbol.asyncIterator](): AsyncIterator<T> {
      const es = new EventSource(url);

      // Close the connection when the query gets cancelled.
      if (signal) {
        signal.addEventListener('abort', () => es.close());
      }

      // FIFO queue that collects incoming chunks between `yield`s.
      const queue: T[] = [];
      let queueResolver: (() => void) | null = null;

      const push = (data: T): void => {
        queue.push(data);
        // Wake up the generator if it is waiting for the next chunk.
        if (queueResolver) {
          queueResolver();
          queueResolver = null;
        }
      };

      const handleMessage = (evt: MessageEvent): void => {
        let parsed: unknown;
        try {
          parsed = JSON.parse(evt.data);
        } catch {
          parsed = evt.data;
        }
        // Include event name so downstream consumers can differentiate types
        push({ event: evt.type, data: parsed } as unknown as T);

        // If server signals stream completion with a custom "done" event,
        // proactively close the EventSource so React Query can transition the
        // fetchStatus from "fetching" to "idle" without waiting for the
        // network layer to time-out.
        if (evt.type === 'done') {
          es.close();
        }
      };

      const handleError = (): void => {
        // Close the stream and wake up the generator to let it finish.
        es.close();
        if (queueResolver) {
          queueResolver();
          queueResolver = null;
        }
      };

      // Attach listeners for all provided event names
      for (const name of eventNames) {
        es.addEventListener(name, handleMessage);
      }
      es.addEventListener('error', handleError);

      try {
        // Loop while the connection is open or there are still queued chunks.
        while (true) {
          // Flush all queued chunks first.
          while (queue.length) {
            yield queue.shift() as T;
          }

          // Break if the stream is closed.
          if (es.readyState === EventSource.CLOSED) {
            break;
          }

          // Wait for the next chunk or a close/error/abort signal.
          await new Promise<void>((resolve) => {
            queueResolver = resolve;
          });
        }
      } finally {
        // Cleanup listeners and close the EventSource.
        for (const name of eventNames) {
          es.removeEventListener(name, handleMessage);
        }
        es.removeEventListener('error', handleError);
        es.close();
      }
    },
  };
}

/**
 * React hook that turns a **Server-Sent Events (EventSource)** endpoint into a
 * TanStack Query "streaming query" powered by the `streamedQuery` helper.
 *
 * Example:
 * ```tsx
 * const { data, fetchStatus } = useSseStreamedQuery(
 *   ['orders', orderId],
 *   `/api/orders/${orderId}/stream`,
 * );
 *
 * if (fetchStatus === 'fetching') {
 *   return <Spinner />; // still streaming
 * }
 *
 * return <OrdersTimeline chunks={data} />;
 * ```
 */
export function useSseStreamedQuery<TChunk = unknown>(
  queryKey: QueryKey,
  url: string,
  {
    enabled = true,
    refetchMode,
    maxChunks,
    initialData,
    eventNames,
  }: UseSseStreamedQueryOptions<TChunk> = {},
): UseQueryResult<TChunk[], Error> {
  return useQuery<TChunk[], Error>({
    queryKey,
    enabled,
    initialData,
    staleTime: Infinity, // avoid reopening the stream on refocus
    // Keep the stream alive only while components use it.
    gcTime: 0,
    queryFn: streamedQuery({
      queryFn: ({ signal }: QueryFunctionContext) => eventSourceToAsyncIterable<TChunk>(url, signal, eventNames),
      refetchMode,
      maxChunks,
    }),
  });
} 