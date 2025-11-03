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
   * Electric SQL base URL used for TanStack DB shape streams
   */
  electricBaseUrl: string;
  /**
   * Enable verbose SSE debug logging in frontend (Vite flag: VITE_DEBUG_SSE)
   */
  debugSse: boolean;
}

export const env: Env = {
  /**
   * API Base URL for backend requests
   */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  queryEngineUrl: import.meta.env.VITE_QUERY_ENGINE_URL || 'http://127.0.0.1:8001',
  workflowOrchestratorUrl: import.meta.env.VITE_WORKFLOW_ORCHESTRATOR_URL || 'http://127.0.0.1:8081',
  knowledgeGraphUrl: import.meta.env.VITE_KNOWLEDGE_GRAPH_URL || 'http://127.0.0.1:7474',
  electricBaseUrl: import.meta.env.VITE_ELECTRIC_BASE_URL || 'http://127.0.0.1:3000',
  debugSse: String(import.meta.env.VITE_DEBUG_SSE).toLowerCase() === 'true',
};
