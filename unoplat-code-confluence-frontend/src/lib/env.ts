/**
 * Environment Variables Helper
 *
 * Provides type-safe access to environment variables with fallbacks.
 */

export interface Env {
  /**
   * API Base URL for backend requests
   */
  apiBaseUrl: string;
  /**
   * Query Engine URL
   */
  queryEngineUrl: string;
  /**
   * Knowledge Graph URL
   */
  knowledgeGraphUrl: string;
  /**
   * Workflow Orchestrator URL
   */
  workflowOrchestratorUrl: string;
  /**
   * Same-origin Electric base path for TanStack DB shape streams.
   * Proxied by Vite (dev) and Nginx (prod) to the Electric service.
   */
  electricBaseUrl: string;
  /**
   * Absolute frontend origin used to resolve same-origin paths when no browser
   * location is available, such as in Node-based tests.
   */
  frontendOrigin?: string;
  /**
   * Enable verbose SSE debug logging in frontend (Vite flag: VITE_DEBUG_SSE)
   */
  debugSse: boolean;
}

export const env: Env = {
  /**
   * API Base URL for backend requests
   */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "/api",
  queryEngineUrl:
    import.meta.env.VITE_QUERY_ENGINE_URL || "/query-engine",
  workflowOrchestratorUrl:
    import.meta.env.VITE_WORKFLOW_ORCHESTRATOR_URL || "http://127.0.0.1:8081",
  knowledgeGraphUrl:
    import.meta.env.VITE_KNOWLEDGE_GRAPH_URL || "http://127.0.0.1:7474",
  // Always same-origin. Do not read VITE_ELECTRIC_BASE_URL — host :3001 is
  // fragile under Tilt/OrbStack and reintroduces CORS/port collisions.
  electricBaseUrl: "/electric",
  frontendOrigin: import.meta.env.VITE_FRONTEND_ORIGIN?.trim() || undefined,
  debugSse: String(import.meta.env.VITE_DEBUG_SSE).toLowerCase() === "true",
};
