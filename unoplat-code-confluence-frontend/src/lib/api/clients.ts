import axios, { AxiosInstance } from "axios";
import { env } from "@/lib/env";

/**
 * Shared axios client for ingestion service (code-confluence-flow-bridge)
 * Base URL: VITE_API_BASE_URL (default: http://127.0.0.1:8000)
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Shared axios client for query engine service
 * Base URL: VITE_QUERY_ENGINE_URL (default: http://127.0.0.1:8001)
 */
export const queryEngineClient: AxiosInstance = axios.create({
  baseURL: env.queryEngineUrl,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});
