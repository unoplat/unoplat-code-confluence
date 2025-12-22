import type { AxiosResponse } from "axios";

import { apiClient } from "@/lib/api/clients";
import { handleApiError } from "@/lib/api";
import type { IssueTracking, ParentWorkflowJobResponse } from "@/types";

import type { AgentFeedbackFormValues, FeedbackCategory, SentimentRating } from "./schema";

/**
 * Agent rating for API submission
 * Matches backend AgentRating model in routers/github_issues/models.py
 */
interface AgentRatingPayload {
  codebase_name: string;
  agent_id: string;
  rating: SentimentRating;
}

/**
 * Request payload for agent feedback submission
 * Matches backend AgentFeedbackSubmissionRequest in routers/github_issues/models.py
 */
export interface AgentFeedbackSubmissionRequest {
  repository_name: string;
  repository_owner_name: string;
  parent_workflow_run_id: string;
  overall_rating: SentimentRating;
  agent_ratings?: AgentRatingPayload[];
  categories: FeedbackCategory[];
  comments?: string;
}

/**
 * Submit agent generation feedback to create a GitHub issue
 *
 * Errors are thrown and should be handled at the useMutation level
 * via onError callback or mutation.error reactive state.
 *
 * @param job - Parent workflow job data providing repository context
 * @param formValues - Form values from TanStack Form
 * @returns Promise with issue tracking response containing GitHub issue details
 * @throws ApiError when request fails (handled by TanStack Query mutation)
 */
export async function submitAgentFeedback(
  job: ParentWorkflowJobResponse,
  formValues: AgentFeedbackFormValues,
): Promise<IssueTracking> {
  // Filter out null ratings and transform to API format
  const agentRatingsPayload: AgentRatingPayload[] = formValues.agentRatings
    .filter((ar): ar is typeof ar & { rating: SentimentRating } => ar.rating !== null)
    .map((ar) => ({
      codebase_name: ar.codebase_name,
      agent_id: ar.agent_id,
      rating: ar.rating,
    }));

  const payload: AgentFeedbackSubmissionRequest = {
    repository_name: job.repository_name,
    repository_owner_name: job.repository_owner_name,
    parent_workflow_run_id: job.repository_workflow_run_id,
    overall_rating: formValues.overallRating,
    agent_ratings: agentRatingsPayload.length > 0 ? agentRatingsPayload : undefined,
    categories: formValues.categories,
    comments: formValues.comments || undefined,
  };

  try {
    const response: AxiosResponse<IssueTracking> = await apiClient.post(
      "/code-confluence/feedback",
      payload,
    );
    return response.data;
  } catch (error: unknown) {
    // Transform and re-throw - TanStack Query mutation handles this
    throw handleApiError(error);
  }
}
