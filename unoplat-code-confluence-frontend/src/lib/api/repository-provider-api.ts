import axios from "axios";
import { ProviderKey } from "@/types/credential-enums";
import type {
  RepositoryProvidersResponse,
  RepositoryProviderFormData,
} from "@/types/repository-provider";
import { apiClient } from "./clients";

/**
 * Fetch configured repository providers from the backend
 *
 * @returns Promise with array of provider keys
 * @throws Error if the request fails
 */
export async function fetchProvidersApi(): Promise<ProviderKey[]> {
  try {
    const { data } = await apiClient.get<RepositoryProvidersResponse>(
      "/repository-providers",
    );
    return data.providers;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail =
        error.response?.data?.detail ?? "Failed to load repository providers";
      throw new Error(detail);
    }
    throw new Error("Unexpected error while loading repository providers");
  }
}

interface IngestTokenResponse {
  message?: string;
}

interface ApiErrorResponse {
  detail: string;
  code?: number;
}

/**
 * Submit provider form data to the API
 *
 * API Contract:
 * - Method: POST
 * - Endpoint: /ingest-token
 * - Query params: namespace, provider_key, secret_kind, url (optional)
 * - Headers: authorization with PAT token
 * - Success: 201 with IngestTokenResponse
 * - Error: 4xx/5xx with ApiErrorResponse containing 'detail' field
 *
 * @param formData - Provider form data including PAT token
 * @returns Promise with success status and optional message
 */
export async function submitProviderForm(
  formData: RepositoryProviderFormData,
): Promise<{ success: boolean; message?: string }> {
  try {
    const { patToken, url, ...requiredParams } = formData;

    const queryParams = {
      namespace: "repository",
      secret_kind: "pat",
      ...requiredParams,
      ...(url && { url }),
    };

    const response = await apiClient.post<IngestTokenResponse>(
      "/ingest-token",
      null,
      {
        params: queryParams,
        headers: {
          Authorization: `Bearer ${patToken}`,
        },
      },
    );
    return { success: true, message: response.data.message };
  } catch (error) {
    if (axios.isAxiosError<ApiErrorResponse>(error)) {
      if (error.response) {
        const errorDetail =
          error.response.data?.detail || "Failed to connect to provider";
        const errorCode = error.response.data?.code;
        const statusCode = error.response.status;

        console.error("API Error Response:", {
          status: statusCode,
          detail: errorDetail,
          code: errorCode,
        });

        return {
          success: false,
          message: errorDetail,
        };
      }
    }
  }
  return { success: false };
}
