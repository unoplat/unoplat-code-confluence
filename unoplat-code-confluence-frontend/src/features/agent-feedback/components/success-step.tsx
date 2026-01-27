import { useEffect } from "react";
import confetti from "canvas-confetti";
import { Check, ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { IssueTracking } from "@/types";

interface SuccessStepProps {
  /** Issue tracking data from successful submission */
  issueData: IssueTracking;
  /** Callback when user clicks close/done */
  onClose: () => void;
}

/**
 * Success step shown after feedback is submitted successfully
 *
 * Displays a celebration confetti animation and confirmation message
 * with option to track the created GitHub issue in a new tab.
 */
export function SuccessStep({
  issueData,
  onClose,
}: SuccessStepProps): React.ReactElement {
  // Fire confetti on mount
  useEffect(() => {
    const fireConfetti = (): void => {
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
    };

    // Small delay to ensure component is visible
    const timeoutId = setTimeout(fireConfetti, 100);

    return () => clearTimeout(timeoutId);
  }, []);

  const handleTrackFeedback = (): void => {
    if (issueData.issue_url) {
      window.open(issueData.issue_url, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 py-8">
      <Card className="w-full max-w-sm border-0 shadow-none">
        <CardHeader className="items-center pb-4 text-center">
          <div className="bg-primary/10 mb-4 flex h-16 w-16 items-center justify-center rounded-full">
            <Check className="text-primary h-8 w-8" />
          </div>
          <CardTitle className="text-xl">Feedback Submitted!</CardTitle>
          <CardDescription>
            Thank you for helping us improve agent generation.
          </CardDescription>
        </CardHeader>

        <CardContent className="flex flex-col items-center gap-6">
          {issueData.issue_number && (
            <Badge variant="completed">Issue #{issueData.issue_number}</Badge>
          )}

          <div className="flex flex-col gap-3 sm:flex-row">
            {issueData.issue_url && (
              <Button variant="default" onClick={handleTrackFeedback}>
                <ExternalLink className="mr-2 h-4 w-4" />
                Track Feedback
              </Button>
            )}
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
