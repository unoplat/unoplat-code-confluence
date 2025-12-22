import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SheetFooter } from "@/components/ui/sheet";
import { useAppForm } from "@/forms";
import type { IssueTracking, ParentWorkflowJobResponse } from "@/types";

import { submitAgentFeedback } from "../api";
import type { AgentFeedbackFormValues, FeedbackCategory } from "../schema";
import {
  FeedbackCategory as FeedbackCategoryEnum,
  FEEDBACK_CATEGORY_LABELS,
} from "../schema";
import { useAgentFeedbackStore } from "../store";
import { getMixedSignalsCount, getSentimentEmoji, getSentimentLabel } from "../utils";

interface DetailsStepProps {
  /** Parent workflow job data for API submission */
  job: ParentWorkflowJobResponse;
  /** Callback when user goes back */
  onBack: () => void;
  /** Callback when submission succeeds */
  onSubmitSuccess: (issueData: IssueTracking) => void;
}

const CATEGORIES = Object.values(FeedbackCategoryEnum) as FeedbackCategory[];
const MAX_COMMENTS_LENGTH = 1000;

/** Category options for CategoryChipsField */
const CATEGORY_OPTIONS: Array<{ value: FeedbackCategory; label: string }> =
  CATEGORIES.map((cat) => ({
    value: cat,
    label: FEEDBACK_CATEGORY_LABELS[cat],
  }));

/**
 * Details step - Second step of feedback flow
 *
 * Owns its form via `useAppForm` for categories and comments fields.
 * Reads rating data from Zustand store (synced by RatingStep).
 * Handles form submission with mutation.
 */
export function DetailsStep({
  job,
  onBack,
  onSubmitSuccess,
}: DetailsStepProps): React.ReactElement {
  const queryClient = useQueryClient();
  const { draft, setDraft } = useAgentFeedbackStore();

  // Read rating data from store (synced by RatingStep)
  const { overallRating, agentRatings } = draft;
  const mixedSignals = getMixedSignalsCount(overallRating, agentRatings);

  // Submission mutation
  const submitMutation = useMutation({
    mutationFn: (values: AgentFeedbackFormValues) =>
      submitAgentFeedback(job, values),
    onSuccess: (issueData) => {
      // Invalidate parent jobs query to refresh feedback_issue_url
      // Note: Query key must match exactly - the actual query uses ["parentWorkflowJobs"] only
      queryClient.invalidateQueries({
        queryKey: ["parentWorkflowJobs"],
      });

      // Show success toast
      toast.success("Feedback submitted successfully", {
        description: issueData.issue_number
          ? `GitHub Issue #${issueData.issue_number} created`
          : undefined,
      });

      // Notify parent
      onSubmitSuccess(issueData);
    },
    onError: (error: Error) => {
      toast.error("Failed to submit feedback", {
        description: error.message || "Please try again later",
      });
    },
  });

  // Create form for categories + comments only
  const form = useAppForm({
    defaultValues: {
      categories: draft.categories,
      comments: draft.comments,
    },
    onSubmit: async ({ value }) => {
      // Combine form values with rating data from store
      const fullPayload: AgentFeedbackFormValues = {
        overallRating,
        agentRatings,
        categories: value.categories,
        comments: value.comments,
      };
      await submitMutation.mutateAsync(fullPayload);
    },
  });

  // Sync form values to store before navigating back
  const handleBack = (): void => {
    setDraft({
      categories: form.state.values.categories,
      comments: form.state.values.comments,
    });
    onBack();
  };

  return (
    <>
      <ScrollArea className="flex-1 px-6">
        <div className="space-y-6 py-4">
          {/* Selected Rating Summary Card */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl" aria-hidden="true">
                    {getSentimentEmoji(overallRating)}
                  </span>
                  <span className="font-medium">
                    {getSentimentLabel(overallRating)}
                  </span>
                </div>
                {mixedSignals > 0 && (
                  <Badge variant="secondary">
                    {mixedSignals} mixed signal{mixedSignals !== 1 ? "s" : ""}
                  </Badge>
                )}
              </div>
            </CardHeader>
            {mixedSignals > 0 && (
              <CardContent className="pt-0">
                <p className="text-muted-foreground text-xs">
                  Some agents were rated differently than your overall rating
                </p>
              </CardContent>
            )}
          </Card>

          {/* Categories Section */}
          <div className="space-y-3">
            <Label className="text-base font-medium">
              What aspects of the agents need improvement?
            </Label>
            <form.AppField name="categories">
              {(field) => (
                <field.CategoryChipsField options={CATEGORY_OPTIONS} />
              )}
            </form.AppField>
          </div>

          {/* Comments Section */}
          <div className="space-y-3">
            <Label className="text-base font-medium">
              Additional comments
              <span className="text-destructive ml-1">*</span>
            </Label>
            <form.AppField
              name="comments"
              validators={{
                onChange: ({ value }) => {
                  if (!value || value.trim().length === 0) {
                    return "Please provide additional comments about your experience";
                  }
                  return undefined;
                },
              }}
            >
              {(field) => (
                <field.TextareaField
                  placeholder="Tell us more about your experience..."
                  maxLength={MAX_COMMENTS_LENGTH}
                />
              )}
            </form.AppField>
          </div>
        </div>
      </ScrollArea>

      <SheetFooter className="flex-row justify-end gap-2 border-t px-6 py-4">
        <Button variant="outline" onClick={handleBack}>
          Back
        </Button>
        <form.Subscribe
          selector={(state) => [state.canSubmit, state.isSubmitting] as const}
        >
          {([canSubmit, isSubmitting]) => (
            <Button
              type="submit"
              disabled={!canSubmit || isSubmitting || submitMutation.isPending}
              onClick={() => form.handleSubmit()}
            >
              {isSubmitting || submitMutation.isPending
                ? "Submitting..."
                : "Submit Feedback"}
            </Button>
          )}
        </form.Subscribe>
      </SheetFooter>
    </>
  );
}
