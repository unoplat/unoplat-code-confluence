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
   * Workflow Orchestrator URL
   */
  workflowOrchestratorUrl: string;
  /**
   * Knowledge Graph URL
   */
  knowledgeGraphUrl: string;
}

export const env: Env = {
  /**
   * API Base URL for backend requests
   */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  workflowOrchestratorUrl: import.meta.env.VITE_WORKFLOW_ORCHESTRATOR_URL || 'http://temporal-ui.code-confluence-flow-bridge.orb.local/namespaces/default/workflows',
  knowledgeGraphUrl: import.meta.env.VITE_KNOWLEDGE_GRAPH_URL || 'http://neo4j.code-confluence-flow-bridge.orb.local/browser/',
}; 