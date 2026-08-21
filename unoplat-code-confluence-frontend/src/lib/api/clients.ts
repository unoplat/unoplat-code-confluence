import axios, { AxiosInstance } from "axios";
import { env } from "@/lib/env";

/**
 * Shared axios client for ingestion service (code-confluence-flow-bridge)
 * Base URL: VITE_API_BASE_URL (default: /api)
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 120000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Shared axios client for query engine service
 * Base URL: VITE_QUERY_ENGINE_URL (default: /query-engine)
 */
export const queryEngineClient: AxiosInstance = axios.create({
  baseURL: env.queryEngineUrl,
  timeout: 120000,
  headers: {
    "Content-Type": "application/json",
  },
});
