import React from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type {
  ParentWorkflowJobResponse,
  FlattenedCodebaseRun,
  GithubRepoStatus,
  ApiErrorReport,
  CodebaseStatus,
  WorkflowStatus,
  WorkflowRun,
} from "@/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { GenerateAgentsProgress } from "@/components/custom/GenerateAgentsProgress";
import { Button } from "@/components/ui/button";
import { GenerateAgentsPreview } from "@/components/custom/GenerateAgentsPreview";
import { AgentStatisticsDisplay } from "@/components/custom/AgentStatisticsDisplay";
import { codebasesToMarkdown } from "@/lib/agent-md-to-markdown";
import { useRepositoryAgentSnapshot } from "@/features/repository-agent-snapshots/hooks";
import { getRepositoryStatus } from "@/lib/api";
import { apiToUiErrorReport } from "@/lib/error-utils";
import { FeedbackDialog } from "@/components/custom/FeedbackDialog";
import { AgentFeedbackSheet } from "@/features/agent-feedback";
import { ButtonGroup } from "@/components/ui/button-group";
import { XCircle, ExternalLink, MessageSquare } from "lucide-react";

// Data structure for aggregated errors (repository + codebase errors combined)
interface AggregatedErrorData {
  repository: GithubRepoStatus;
  failedCodebases: FlattenedCodebaseRun[];
}

// Define FeedbackSource type to match the one in FeedbackDialog
type FeedbackSource =
  | { type: "codebase"; data: FlattenedCodebaseRun }
  | { type: "repository"; data: GithubRepoStatus }
  | { type: "aggregated"; data: AggregatedErrorData };

interface GenerateAgentsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Job data for viewing progress/results */
  job: ParentWorkflowJobResponse | null;
}

/**
 * Dialog for viewing Agent MD generation/update progress and results.
 * This is a view-only component - it does not trigger runs.
 *
 * Data Sources:
 * - Status: job.status from REST API (already available from table row)
 * - Progress/Events/Output: Electric SQL real-time sync via useRepositoryAgentSnapshot
 */
export function GenerateAgentsDialog({
  open,
  onOpenChange,
  job,
}: GenerateAgentsDialogProps): React.ReactElement | null {
  const [isPreviewOpen, setIsPreviewOpen] = React.useState<boolean>(false);
  const [feedbackDialogOpen, setFeedbackDialogOpen] =
    React.useState<boolean>(false);
  const [feedbackSource, setFeedbackSource] =
    React.useState<FeedbackSource | null>(null);
  const [agentFeedbackSheetOpen, setAgentFeedbackSheetOpen] =
    React.useState<boolean>(false);
  const queryClient = useQueryClient();

  // Build scope for Electric SQL query - requires runId from job
  const scope = React.useMemo(() => {
    if (!job) return null;
    return {
      owner: job.repository_owner_name,
      repository: job.repository_name,
      runId: job.repository_workflow_run_id,
    };
  }, [job]);

  // Electric SQL hook for real-time progress data
  const {
    parsedSnapshot,
    isLoading: isLiveLoading,
    isError: isLiveError,
    isReady: isLiveReady,
    status: liveStatus,
    collection,
  } = useRepositoryAgentSnapshot(open ? scope : null);

  // Derive codebaseIds from Electric SQL snapshot
  const codebaseIds = React.useMemo(
    () => parsedSnapshot?.codebases?.map((cb) => cb.codebaseName) ?? [],
    [parsedSnapshot?.codebases],
  );

  // Derive preview content from Electric SQL snapshot
  const previewCodebases = parsedSnapshot?.markdownByCodebase;
  const hasPreviewContent =
    previewCodebases && Object.keys(previewCodebases).length > 0;

  const previewContent = React.useMemo(() => {
    if (!job || !hasPreviewContent || !previewCodebases) {
      return null;
    }
    return codebasesToMarkdown(previewCodebases, {
      title: `AGENTS.md - ${job.repository_owner_name}/${job.repository_name}`,
    });
  }, [job, hasPreviewContent, previewCodebases]);

  // Derive status from job prop (REST API source)
  const jobStatus = job?.status ?? "SUBMITTED";
  const isRunning = jobStatus === "RUNNING" || jobStatus === "SUBMITTED";
  const isCompleted = jobStatus === "COMPLETED";
  // ERROR = partial failure (some agents succeeded, some failed)
  const isFailed = jobStatus === "FAILED" || jobStatus === "ERROR";

  // Fetch repository status ONLY when job has failed (to get error details)
  // Electric SQL snapshot does NOT contain error data - must fetch via REST API
  const { data: repositoryStatus } = useQuery({
    queryKey: [
      "repositoryStatus",
      job?.repository_name,
      job?.repository_owner_name,
      job?.repository_workflow_run_id,
    ],
    queryFn: async () => {
      if (!job) return null;
      const status = await getRepositoryStatus(
        job.repository_name,
        job.repository_owner_name,
        job.repository_workflow_run_id,
      );
      // Convert API error report to UI error report if present
      if (status.error_report) {
        status.error_report = apiToUiErrorReport(
          status.error_report as ApiErrorReport,
          {
            error_type: "REPOSITORY",
            repository_name: status.repository_name,
            repository_owner_name: status.repository_owner_name,
            parent_workflow_run_id: status.repository_workflow_run_id,
          },
        );
      }
      return status;
    },
    enabled: open && isFailed && !!job, // CONDITIONAL: only fetch when failed
    staleTime: 5000,
  });

  // Show statistics only when completed and data available
  const showStatistics = isCompleted && parsedSnapshot?.statistics;

  // Transform nested codebase structure to flat array of failed runs with UI error reports
  const failedCodebaseRuns = React.useMemo((): FlattenedCodebaseRun[] => {
    if (!repositoryStatus?.codebase_status_list?.codebases) return [];

    return repositoryStatus.codebase_status_list.codebases.flatMap(
      (codebase: CodebaseStatus) => {
        return codebase.workflows.flatMap((workflow: WorkflowStatus) => {
          return workflow.codebase_workflow_runs
            .filter((run: WorkflowRun) => run.status === "FAILED" || run.status === "ERROR")
            .map((run: WorkflowRun): FlattenedCodebaseRun => {
              const uiErrorReport = run.error_report
                ? apiToUiErrorReport(run.error_report, {
                    error_type: "CODEBASE",
                    repository_name: repositoryStatus.repository_name,
                    repository_owner_name:
                      repositoryStatus.repository_owner_name,
                    parent_workflow_run_id:
                      repositoryStatus.repository_workflow_run_id,
                    workflow_id: workflow.codebase_workflow_id,
                    workflow_run_id: run.codebase_workflow_run_id,
                  })
                : null;
              return {
                codebase_folder: codebase.codebase_folder,
                codebase_workflow_run_id: run.codebase_workflow_run_id,
                codebase_status: run.status,
                codebase_started_at: run.started_at,
                codebase_completed_at: run.completed_at,
                codebase_error_report: uiErrorReport,
                codebase_issue_tracking: run.issue_tracking,
              };
            });
        });
      },
    );
  }, [repositoryStatus]);

  // Check if repository has a reportable error (failed/error + has error report + no issue yet)
  const hasReportableRepositoryError = React.useMemo(() => {
    if (!repositoryStatus) return false;
    const isErrorState = repositoryStatus.status === "FAILED" || repositoryStatus.status === "ERROR";
    return (
      isErrorState &&
      !!repositoryStatus.error_report &&
      !repositoryStatus.issue_tracking?.issue_url
    );
  }, [repositoryStatus]);

  // Check if there are ANY reportable errors (repository or codebase level)
  const hasAnyReportableError = React.useMemo(() => {
    // If repository-level issue exists, it covers ALL errors (aggregated submission)
    // No need to show "Submit Error" - all errors are already tracked
    if (repositoryStatus?.issue_tracking?.issue_url) return false;

    // Check repository-level error
    if (hasReportableRepositoryError) return true;

    // Check codebase-level errors (any failed codebase with error report and no issue)
    const hasReportableCodebaseErrors = failedCodebaseRuns.some(
      (run) =>
        run.codebase_error_report && !run.codebase_issue_tracking?.issue_url,
    );

    return hasReportableCodebaseErrors;
  }, [repositoryStatus?.issue_tracking?.issue_url, hasReportableRepositoryError, failedCodebaseRuns]);

  // Get the tracked issue URL (prefer repository-level, fallback to first codebase with issue)
  const trackedIssueUrl = React.useMemo((): string | null => {
    // Check repository-level issue first
    if (repositoryStatus?.issue_tracking?.issue_url) {
      return repositoryStatus.issue_tracking.issue_url;
    }
    // Fallback to first codebase with a tracked issue
    const codebaseWithIssue = failedCodebaseRuns.find(
      (run) => run.codebase_issue_tracking?.issue_url,
    );
    return codebaseWithIssue?.codebase_issue_tracking?.issue_url ?? null;
  }, [repositoryStatus, failedCodebaseRuns]);

  // Handle aggregated feedback submission (single button for all errors)
  const handleSubmitAggregatedFeedback = (): void => {
    if (!repositoryStatus) return;

    setFeedbackSource({
      type: "aggregated",
      data: {
        repository: repositoryStatus,
        failedCodebases: failedCodebaseRuns,
      },
    });
    setFeedbackDialogOpen(true);
  };

  // Handle feedback success - invalidate query to refresh data
  const handleFeedbackSuccess = (): void => {
    queryClient.invalidateQueries({
      queryKey: [
        "repositoryStatus",
        job?.repository_name,
        job?.repository_owner_name,
        job?.repository_workflow_run_id,
      ],
    });
  };

  const handleDownloadAll = (): void => {
    if (!previewContent) {
      return;
    }

    const blob = new Blob([previewContent], {
      type: "text/markdown;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "AGENTS.md";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (!job) {
    return null;
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="flex max-h-[85vh] flex-col p-6 sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>AGENTS.md</DialogTitle>
          <DialogDescription>
            Track generation progress, preview results, and view usage
            statistics.
          </DialogDescription>
        </DialogHeader>

        {/* Section: Run Details */}
        <div className="mt-6 mb-4 flex justify-center">
          <Badge variant="section">Run Details</Badge>
        </div>

        <Card className="p-4 space-y-3">
          <div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide">
              Repository
            </div>
            <div className="text-sm font-medium">
              {job.repository_owner_name}/{job.repository_name}
            </div>
          </div>
          <div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide">
              Run ID
            </div>
            <div className="text-muted-foreground font-mono text-xs">
              {job.repository_workflow_run_id}
            </div>
          </div>
        </Card>

        {/* Section: Progress */}
        <div className="mt-6 mb-4 flex justify-center">
          <Badge variant="section">Progress</Badge>
        </div>

        {/* Main Content Area */}
        <div className="flex min-h-0 flex-1 flex-col overflow-y-auto">
          {/* Loading State */}
          {isLiveLoading && !isLiveReady && (
            <div className="text-sm">Connecting to real-time updates...</div>
          )}

          {/* Error State */}
          {isLiveError && (
            <div className="space-y-2" role="alert">
              <div className="text-sm text-red-600">
                Electric sync encountered an error.
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const restart = async (): Promise<void> => {
                      if (!collection) {
                        return;
                      }

                      await collection.cleanup();
                      if (collection.utils.clearError) {
                        collection.utils.clearError();
                      }
                      await collection.preload();
                    };

                    void restart();
                  }}
                >
                  Retry Sync
                </Button>
                <div className="text-muted-foreground text-xs">
                  Status: {liveStatus}
                </div>
              </div>
            </div>
          )}


          {/* Progress Display - shown when we have codebaseIds */}
          {codebaseIds.length > 0 && (
            <GenerateAgentsProgress
              snapshot={parsedSnapshot}
              codebaseIds={codebaseIds}
              isSyncing={isLiveLoading || isRunning}
            />
          )}

          {/* Waiting for data state */}
          {!isLiveError && codebaseIds.length === 0 && isRunning && (
            <div className="text-muted-foreground py-8 text-center">
              <p>Waiting for workflow to start...</p>
              <p className="mt-2 text-sm">
                Real-time updates will appear automatically.
              </p>
            </div>
          )}

          {/* Statistics Display (for completed jobs) */}
          {showStatistics && parsedSnapshot?.statistics && (
            <>
              {/* Section: Statistics */}
              <div className="mt-6 mb-4 flex justify-center">
                <Badge variant="section">Statistics</Badge>
              </div>
              <AgentStatisticsDisplay statistics={parsedSnapshot.statistics} />
            </>
          )}
        </div>

        {/* Footer Actions */}
        <div className="mt-6 flex items-center justify-between gap-3">
          {/* Left side: Status + Actions based on job state */}
          {isFailed ? (
            <ButtonGroup>
              <Badge
                variant="failed"
                className="gap-1 rounded-md border-destructive/30"
              >
                <XCircle className="h-3 w-3" />
                Failed
              </Badge>
              {hasAnyReportableError ? (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleSubmitAggregatedFeedback}
                >
                  Submit Error
                </Button>
              ) : trackedIssueUrl ? (
                <Button size="sm" variant="outline" asChild>
                  <a
                    href={trackedIssueUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink className="mr-1.5 h-3 w-3" />
                    Track Error
                  </a>
                </Button>
              ) : null}
            </ButtonGroup>
          ) : isCompleted ? (
            // Completed state: Show Give Feedback or Track Feedback button
            job.feedback_issue_url ? (
              <Button size="sm" variant="outline" asChild>
                <a
                  href={job.feedback_issue_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="mr-1.5 h-3 w-3" />
                  Track Feedback
                </a>
              </Button>
            ) : (
              <Button
                size="sm"
                variant="outline"
                onClick={() => setAgentFeedbackSheetOpen(true)}
              >
                <MessageSquare className="mr-1.5 h-3 w-3" />
                Give Feedback
              </Button>
            )
          ) : (
            <div />
          )}

          {/* Right side: Preview Result */}
          <Button
            size="sm"
            disabled={!hasPreviewContent || isRunning}
            onClick={() => setIsPreviewOpen(true)}
          >
            Preview Result
          </Button>
        </div>

          {/* Preview Dialog */}
          {hasPreviewContent && previewCodebases && (
            <GenerateAgentsPreview
              codebases={previewCodebases}
              repositoryName={`${job.repository_owner_name}/${job.repository_name}`}
              open={isPreviewOpen}
              onOpenChange={setIsPreviewOpen}
              onDownloadAll={handleDownloadAll}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Feedback Dialog for aggregated error reporting */}
      <FeedbackDialog
        open={feedbackDialogOpen}
        onOpenChange={setFeedbackDialogOpen}
        source={feedbackSource}
        operationType={job.operation}
        onSuccess={handleFeedbackSuccess}
      />

      {/* Agent Feedback Sheet for rating agent generation quality */}
      {parsedSnapshot?.codebases && (
        <AgentFeedbackSheet
          open={agentFeedbackSheetOpen}
          onOpenChange={setAgentFeedbackSheetOpen}
          job={job}
          codebases={parsedSnapshot.codebases}
        />
      )}
    </>
  );
}
