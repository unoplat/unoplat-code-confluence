import axios from "axios";
import { queryEngineClient } from "./clients";
import type {
  ToolConfigResponse,
  ToolConfigListResponse,
  ToolProvider,
} from "@/features/tool-config/types";
import {
  toolConfigResponseSchema,
  toolConfigListResponseSchema,
} from "@/features/tool-config/types";
import { handleApiError } from "@/lib/api";

/**
 * Fetch all tool configurations
 * @returns List of tool configurations with their status
 */
export async function getToolConfigs(): Promise<ToolConfigListResponse> {
  const response = await queryEngineClient.get("/v1/tool-config");
  return toolConfigListResponseSchema.parse(response.data);
}

/**
 * Fetch a single tool configuration by provider
 * @param provider - The tool provider identifier
 * @returns Tool configuration status or null if not found
 */
export async function getToolConfig(
  provider: ToolProvider,
): Promise<ToolConfigResponse | null> {
  try {
    const response = await queryEngineClient.get(`/v1/tool-config/${provider}`);
    return toolConfigResponseSchema.parse(response.data);
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw handleApiError(error);
  }
}

/**
 * Save tool configuration (API key)
 * @param provider - The tool provider identifier
 * @param apiKey - The API key to save
 * @returns Updated tool configuration status
 */
export async function saveToolConfig(
  provider: ToolProvider,
  apiKey: string,
): Promise<ToolConfigResponse> {
  // Trim API key before sending
  const sanitizedApiKey = apiKey.trim();

  const response = await queryEngineClient.put(
    `/v1/tool-config/${provider}`,
    null,
    {
      headers: { Authorization: `Bearer ${sanitizedApiKey}` },
    },
  );
  return toolConfigResponseSchema.parse(response.data);
}

/**
 * Delete tool configuration
 * @param provider - The tool provider identifier
 * @returns Success response
 */
export async function deleteToolConfig(
  provider: ToolProvider,
): Promise<{ message: string }> {
  const response = await queryEngineClient.delete(
    `/v1/tool-config/${provider}`,
  );
  return response.data;
}
