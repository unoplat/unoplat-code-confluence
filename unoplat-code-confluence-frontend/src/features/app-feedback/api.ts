import type { AxiosResponse } from "axios";

import { queryEngineClient } from "@/lib/api/clients";
import { handleApiError } from "@/lib/api";

import type { AppFeedbackCategory, SentimentRating } from "./schema";

/**
 * Request payload for app feedback submission
 * Matches backend AppFeedbackRequest model
 */
export interface AppFeedbackRequest {
  category: AppFeedbackCategory;
  sentiment: SentimentRating;
  subject: string;
  description: string;
  current_route?: string;
  app_version?: string;
}

/**
 * Response from app feedback submission
 * Matches backend AppFeedbackResponse model
 */
export interface AppFeedbackResponse {
  issue_url: string | null;
  issue_number: number | null;
}

/**
 * Submit general app feedback to create a GitHub issue
 *
 * @param payload - Feedback request data
 * @returns Promise with issue tracking response
 * @throws ApiError when request fails (handled by TanStack Query mutation)
 */
export async function submitAppFeedback(
  payload: AppFeedbackRequest,
): Promise<AppFeedbackResponse> {
  try {
    const response: AxiosResponse<AppFeedbackResponse> =
      await queryEngineClient.post("/v1/app-feedback", payload);
    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
}
