import { useCallback, useState } from "react";

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import type { IssueTracking, ParentWorkflowJobResponse } from "@/types";
import type { RepositoryAgentCodebaseState } from "@/features/repository-agent-snapshots/transformers";

import { FeedbackStep } from "../schema";
import { useAgentFeedbackStore } from "../store";
import { DetailsStep } from "./details-step";
import { RatingStep } from "./rating-step";
import { SuccessStep } from "./success-step";

interface AgentFeedbackSheetProps {
  /** Whether the sheet is open */
  open: boolean;
  /** Callback when open state changes */
  onOpenChange: (open: boolean) => void;
  /** Parent workflow job data */
  job: ParentWorkflowJobResponse;
  /** Codebases from the agent snapshot */
  codebases: RepositoryAgentCodebaseState[];
}

/**
 * Agent feedback sheet component
 *
 * Pure coordinator that orchestrates the multi-step feedback flow.
 * Each step (RatingStep, DetailsStep) owns its own form via useAppForm.
 * Draft persistence handled via Zustand store.
 *
 * Flow: Rating Step → Details Step → Success Step
 */
export function AgentFeedbackSheet({
  open,
  onOpenChange,
  job,
  codebases,
}: AgentFeedbackSheetProps): React.ReactElement {
  // Zustand store for step navigation and draft persistence
  const { step, setStep, reset: resetStore } = useAgentFeedbackStore();

  // Track submitted issue data for success step
  const [submittedIssue, setSubmittedIssue] = useState<IssueTracking | null>(
    null,
  );

  // Step navigation handlers
  const handleContinue = useCallback((): void => {
    // RatingStep syncs its values to store before calling this
    setStep(FeedbackStep.DETAILS);
  }, [setStep]);

  const handleBack = useCallback((): void => {
    // DetailsStep syncs its values to store before calling this
    setStep(FeedbackStep.RATING);
  }, [setStep]);

  // Handle successful submission from DetailsStep
  const handleSubmitSuccess = useCallback(
    (issueData: IssueTracking): void => {
      setSubmittedIssue(issueData);
      setStep(FeedbackStep.SUCCESS);
    },
    [setStep],
  );

  // Handle sheet close
  const handleClose = useCallback((): void => {
    // On success step, reset the store since feedback was submitted
    if (step === FeedbackStep.SUCCESS) {
      resetStore();
      setSubmittedIssue(null);
    }
    // Draft values are auto-synced by steps on navigation, no sync needed here
    onOpenChange(false);
  }, [step, resetStore, onOpenChange]);

  // Handle cancel from rating step (no draft save)
  const handleCancel = useCallback((): void => {
    onOpenChange(false);
  }, [onOpenChange]);

  // Determine current step content
  const renderStepContent = (): React.ReactElement => {
    switch (step) {
      case FeedbackStep.RATING:
        return (
          <RatingStep
            codebases={codebases}
            job={job}
            onCancel={handleCancel}
            onContinue={handleContinue}
          />
        );
      case FeedbackStep.DETAILS:
        return (
          <DetailsStep
            job={job}
            onBack={handleBack}
            onSubmitSuccess={handleSubmitSuccess}
          />
        );
      case FeedbackStep.SUCCESS:
        if (submittedIssue) {
          return (
            <SuccessStep issueData={submittedIssue} onClose={handleClose} />
          );
        }
        // Fallback - shouldn't happen
        return (
          <SuccessStep
            issueData={{ issue_url: null, issue_number: null }}
            onClose={handleClose}
          />
        );
      default:
        return (
          <RatingStep
            codebases={codebases}
            job={job}
            onCancel={handleCancel}
            onContinue={handleContinue}
          />
        );
    }
  };

  // Get step title and description
  const getStepHeader = (): { title: string; description: string } => {
    switch (step) {
      case FeedbackStep.RATING:
        return {
          title: "Rate Your Experience",
          description:
            "Help us improve agent generation by sharing your feedback",
        };
      case FeedbackStep.DETAILS:
        return {
          title: "Additional Details",
          description: "Select categories and add comments (optional)",
        };
      case FeedbackStep.SUCCESS:
        return {
          title: "Thank You!",
          description: "Your feedback has been submitted",
        };
      default:
        return {
          title: "Agent Feedback",
          description: "Share your experience with agent generation",
        };
    }
  };

  const { title, description } = getStepHeader();

  return (
    <Sheet open={open} onOpenChange={handleClose}>
      <SheetContent
        side="right"
        size="lg"
        className="flex flex-col gap-0 overflow-hidden p-0"
      >
        <SheetHeader className="flex-shrink-0 border-b px-6 py-4">
          <SheetTitle>{title}</SheetTitle>
          <SheetDescription>{description}</SheetDescription>
        </SheetHeader>

        {renderStepContent()}
      </SheetContent>
    </Sheet>
  );
}
