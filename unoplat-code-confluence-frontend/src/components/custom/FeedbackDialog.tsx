import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "../ui/dialog";
import { Button } from "../ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Textarea } from "../ui/textarea";
import { Card } from "../ui/card";
import { Separator } from "../ui/separator";
import { useMutation } from "@tanstack/react-query";
import type { FlattenedCodebaseRun, UiErrorReport, IssueType, GithubRepoStatus, IssueTracking, IssueStatus } from "../../types";
import ReactMarkdown from "react-markdown";
import { toast } from "../ui/use-toast";
import { Plus } from "lucide-react";
import { Label } from "../ui/label";

// Import API submission function and utilities
import { submitFeedback } from "../../lib/api";
import { formatErrorReportContent } from "../../lib/error-utils";
import { IssueCreatedDialog } from "./IssueCreatedDialog";

// Union type for different feedback sources
type FeedbackSource = 
  | { type: 'codebase'; data: FlattenedCodebaseRun }
  | { type: 'repository'; data: GithubRepoStatus };

interface FeedbackDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  source: FeedbackSource | null;
  onSuccess?: () => void;
}

export function FeedbackDialog({
  open,
  onOpenChange,
  source,
  onSuccess
}: FeedbackDialogProps): React.ReactElement | null {
  const [content, setContent] = useState<string>("");
  const [activeTab, setActiveTab] = useState<string>("edit");
  const [createdIssue, setCreatedIssue] = useState<IssueTracking | null>(null);
  const [showSuccessDialog, setShowSuccessDialog] = useState<boolean>(false);

  // Get appropriate title based on feedback source type
  const getDialogTitle = (): string => {
    if (!source) return "Submit Feedback";
    return source.type === 'codebase' 
      ? "Submit Codebase Feedback" 
      : "Submit Repository Feedback";
  };

  // Initialize with error report content if available
  React.useEffect(() => {
    if (!source) {
      setContent("");
      return;
    }

    let errorReport: UiErrorReport | null | undefined;
    
    if (source.type === 'codebase') {
      errorReport = source.data.codebase_error_report;
    } else {
      errorReport = source.data.error_report;
    }

    if (errorReport) {
      // Use the utility function to format the error report
      const formattedContent = formatErrorReportContent(errorReport);
      setContent(formattedContent);
    } else {
      setContent("");
    }
  }, [source]);

  // Set up mutation for submitting feedback
  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!source) return null;
      
      // Determine issue type based on source type
      const issueType: IssueType = source.type === 'codebase' ? "CODEBASE" : "REPOSITORY";
      
      if (source.type === 'codebase') {
        const codebaseRun = source.data;
        
        // Check if issue is already submitted through issue_tracking field
        if (codebaseRun.codebase_issue_tracking?.issue_url) {
          toast.info("This issue has already been submitted.");
          return codebaseRun.codebase_issue_tracking;
        }
        
        const report = codebaseRun.codebase_error_report;
        if (!report) throw new Error('No error report available');

        return submitFeedback({
          repository_name: report.repository_name,
          repository_owner_name: report.repository_owner_name,
          parent_workflow_run_id: report.parent_workflow_run_id,
          error_type: issueType,
          codebase_folder: codebaseRun.codebase_folder,
          codebase_workflow_run_id: codebaseRun.codebase_workflow_run_id,
          error_message_body: content
        });
      } else {
        const repoStatus = source.data;
        
        // Check if issue is already submitted through issue_tracking field
        if (repoStatus.issue_tracking?.issue_url) {
          toast.info("This issue has already been submitted.");
          return repoStatus.issue_tracking;
        }
        
        if (!repoStatus.error_report) throw new Error('No error report available');

        return submitFeedback({
          repository_name: repoStatus.repository_name,
          repository_owner_name: repoStatus.repository_owner_name,
          parent_workflow_run_id: repoStatus.repository_workflow_run_id,
          error_type: issueType,
          codebase_folder: null, // No specific codebase folder for repository-level issues
          codebase_workflow_run_id: null, // No specific codebase run ID for repository-level issues
          error_message_body: content
        });
      }
    },
    onSuccess: (data) => {
      // Only show toaster for errors, not for success
      if (!data) {
        toast.error("Failed to create issue: No response data");
        return;
      }
      
      // Convert API IssueTracking to our internal IssueTracking type
      // The main difference is that issue_status is string in API but IssueStatus enum in our types
      const issueData: IssueTracking = {
        ...data,
        issue_status: data.issue_status as IssueStatus | null | undefined
      };
      
      // Store the created issue and show the success dialog
      setCreatedIssue(issueData);
      onOpenChange(false); // Close the feedback dialog
      setShowSuccessDialog(true);
      
      // Call the onSuccess callback if provided
      if (onSuccess) onSuccess();
    },
    onError: (error) => {
      toast.error(
        `Failed to create issue: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  });

  const handleSubmit = () => {
    submitMutation.mutate();
  };

  const handleSuccessDialogClose = () => {
    setShowSuccessDialog(false);
    setCreatedIssue(null);
  };

  if (!source) return null;

  // Get appropriate label based on feedback source type
  const contentLabel = source.type === 'codebase' 
    ? "Codebase Error Description" 
    : "Repository Error Description";

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{getDialogTitle()}</DialogTitle>
          </DialogHeader>

          <Card className="w-full">
            <Tabs
              defaultValue="edit"
              value={activeTab}
              onValueChange={setActiveTab}
              className="w-full"
            >
              <TabsList>
                <TabsTrigger value="edit">Edit</TabsTrigger>
                <TabsTrigger value="preview">Preview</TabsTrigger>
              </TabsList>
              
              <TabsContent value="edit" className="space-y-4 p-4">
                <div className="space-y-2">
                  <Label htmlFor="content">{contentLabel}</Label>
                  <Textarea
                    id="content"
                    placeholder="Describe the error and any additional context..."
                    className="min-h-[400px] font-mono text-sm"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                  />
                </div>
              </TabsContent>
              
              <TabsContent value="preview" className="space-y-4 p-4">
                <div className="min-h-[400px] rounded-md border p-4 prose dark:prose-invert prose-sm max-w-none overflow-auto">
                  <ReactMarkdown>{content}</ReactMarkdown>
                </div>
              </TabsContent>
            </Tabs>
          </Card>
          
          <Separator />
          
          <DialogFooter className="gap-2">
            <Button 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              disabled={submitMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="default"
              onClick={handleSubmit}
              disabled={submitMutation.isPending}
            >
              {submitMutation.isPending ? (
                <>
                  <span className="animate-spin mr-2">&#8635;</span>
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Issue
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Show success dialog when we have created an issue */}
      {createdIssue && (
        <IssueCreatedDialog
          isOpen={showSuccessDialog}
          onClose={handleSuccessDialogClose}
          issueTracking={createdIssue}
        />
      )}
    </>
  );
} 