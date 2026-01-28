import type { ToolProvider } from "./types";

/**
 * Display names for tool providers
 */
export const TOOL_PROVIDER_DISPLAY_NAMES: Record<ToolProvider, string> = {
  exa: "Exa Search",
} as const;

/**
 * Help/documentation URLs for tool providers
 */
export const TOOL_PROVIDER_HELP_URLS: Record<ToolProvider, string> = {
  exa: "https://docs.exa.ai/reference/getting-started",
} as const;

/**
 * Descriptions for tool providers
 */
export const TOOL_PROVIDER_DESCRIPTIONS: Record<ToolProvider, string> = {
  exa: "AI-powered search engine for finding relevant web content and documentation",
} as const;
