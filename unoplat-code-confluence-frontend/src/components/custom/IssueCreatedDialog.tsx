import { ReactElement } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "../ui/dialog";
import { Button } from "../ui/button";
import { Check } from "lucide-react";
import { IssueTracking } from "../../types";

interface IssueCreatedDialogProps {
  isOpen: boolean;
  onClose: () => void;
  issueTracking: IssueTracking;
}

/**
 * Dialog component shown after successfully creating an issue
 * 
 * @param props.isOpen - Whether the dialog is open
 * @param props.onClose - Function to close the dialog
 * @param props.issueTracking - The issue tracking data returned from API
 * @returns Dialog component with success message and issue details
 */
export function IssueCreatedDialog({
  isOpen,
  onClose,
  issueTracking
}: IssueCreatedDialogProps): ReactElement {
  const { issue_number, issue_url } = issueTracking;

  const handleViewOnGitHub = () => {
    if (issue_url) {
      window.open(issue_url, "_blank");
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 mb-4">
            <Check className="h-6 w-6 text-primary" />
          </div>
          <DialogTitle className="text-center text-lg font-semibold">
            Issue created #{issue_number}
          </DialogTitle>
          <DialogDescription className="text-center">
            Your feedback has been submitted as a GitHub issue for tracking and resolution.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col items-center justify-center p-4 text-center">
          <p className="text-sm text-muted-foreground mb-4">
            Your issue has been successfully created and is being tracked.
          </p>
        </div>
        <DialogFooter className="sm:justify-center">
          <Button 
            variant="outline" 
            onClick={onClose}
            className="mr-2"
          >
            Close
          </Button>
          {issue_url && (
            <Button 
              variant="default"
              onClick={handleViewOnGitHub}
            >
              View on GitHub
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 