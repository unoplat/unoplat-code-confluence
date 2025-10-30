import type { IngestedRepository } from "../types";

export interface SSEEvent {
  id: number;
  event: string; // Format: "{codebase}:{agent}:{activity}" or "status"
  data: SSEEventData;
}

export interface SSEEventData {
  message: string;
  timestamp?: string;
  status?: string;
  tool?: string;
  args?: string;
  preview?: string;
  prompt_preview?: string;
  repository?: string;
  thinking_start?: number;
}

export interface ParsedSSEEvent extends SSEEvent {
  codebase?: string;
  agent?: string;
  activity?: string;
  isStatusEvent: boolean;
}

export type AgentType =
  | "project_configuration_agent"
  | "development_workflow"
  | "business_logic_domain";

export type ActivityType =
  | "prompt.start"
  | "model.request"
  | "tool.call"
  | "tool.result"
  | "result"
  | "complete";

export interface CodebaseProgress {
  codebaseId: string;
  codebaseName: string;
  agents: Map<AgentType, AgentProgress>;
  overallProgress: number;
  status: "initializing" | "processing" | "completed" | "error";
  events: SSEEvent[];
  startTime: Date;
}

export interface AgentProgress {
  agentType: AgentType;
  status: "idle" | "running" | "completed" | "error";
  events: SSEEventData[];
  lastActivity?: ActivityType;
  progress: number;
  currentTool?: string;
  lastUpdate?: Date;
}

export interface GenerationContext {
  repository: IngestedRepository;
  codebases: string[];
  startTime: Date;
  isComplete: boolean;
  generatedContent?: string;
}

// ================================
// Aggregated repository event types
// ================================

export interface AgentMdOutputProgrammingLanguageMetadata {
  primary_language: string;
  package_manager: string;
}

export interface AgentMdOutputProjectConfigurationFile {
  path: string;
  purpose: string;
}

export interface AgentMdOutputProjectConfiguration {
  config_files: AgentMdOutputProjectConfigurationFile[];
}

export interface AgentMdOutputDevelopmentCommand {
  kind: string;
  command: string;
  description?: string;
  config_files: string[];
}

export interface AgentMdOutputDevelopmentWorkflow {
  commands: AgentMdOutputDevelopmentCommand[];
}

export interface AgentMdOutputBusinessLogicFile {
  path: string;
  responsibility?: string;
}

export interface AgentMdOutputBusinessLogic {
  description: string;
  data_models: AgentMdOutputBusinessLogicFile[];
}

export interface AgentMdOutput {
  programming_language_metadata: AgentMdOutputProgrammingLanguageMetadata;
  project_configuration: AgentMdOutputProjectConfiguration;
  development_workflow: AgentMdOutputDevelopmentWorkflow;
  business_logic: AgentMdOutputBusinessLogic;
}

export interface AggregatedAgentsMdEventData {
  repository: string;
  codebases: Record<string, string>; // Values are stringified JSON of AgentMdOutput
}

export interface AggregatedSSEEvent {
  id: number;
  event: string; // "{repository_qualified_name}:aggregated_final_summary_agent:agent_md_output"
  data: AggregatedAgentsMdEventData;
}
