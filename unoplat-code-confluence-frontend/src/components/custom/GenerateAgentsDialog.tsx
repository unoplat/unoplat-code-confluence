import React from "react";
import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import type {
  ParentWorkflowJobResponse,
  FlattenedCodebaseRun,
  GithubRepoStatus,
  ApiErrorReport,
  CodebaseStatus,
  WorkflowStatus,
  WorkflowRun,
  JobStatus,
  RepositoryWorkflowOperation,
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
import { GenerateAgentsProgressLive } from "@/components/custom/GenerateAgentsProgressLive";
import { Button } from "@/components/ui/button";
import { GenerateAgentsPreview } from "@/components/custom/GenerateAgentsPreview";
import { AgentStatisticsDisplay } from "@/components/custom/AgentStatisticsDisplay";
import { codebasesToMarkdown } from "@/lib/agent-md-to-markdown";
import {
  useRepositoryAgentCodebaseProgress,
  useRepositoryAgentSnapshot,
} from "@/features/repository-agent-snapshots/hooks";
import type { RepositoryAgentMdPrStatusResponse } from "@/lib/api";
import {
  cancelRepositoryAgentRun,
  createRepositoryAgentMdPr,
  getParentWorkflowJobs,
  getRepositoryAgentMdPrStatus,
  getRepositoryStatus,
} from "@/lib/api";
import { apiToUiErrorReport } from "@/lib/error-utils";
import { FeedbackDialog } from "@/components/custom/FeedbackDialog";
import { AgentFeedbackSheet } from "@/features/agent-feedback";
import { ButtonGroup } from "@/components/ui/button-group";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { XCircle, ExternalLink, MessageSquare } from "lucide-react";
import { toast } from "sonner";

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

function getApiErrorMessage(error: unknown, fallbackMessage: string): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    typeof error.message === "string"
  ) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallbackMessage;
}

function isInFlightJobStatus(status: JobStatus): boolean {
  return (
    status === "SUBMITTED" || status === "RUNNING" || status === "RETRYING"
  );
}

function isAgentWorkflowOperation(
  operation: RepositoryWorkflowOperation,
): boolean {
  return operation === "AGENTS_GENERATION" || operation === "AGENT_MD_UPDATE";
}

/**
 * Dialog for viewing Agent MD generation/update progress and results.
 * This is a view-only component - it does not trigger runs.
 *
 * Data Sources:
 * - Status: job.status from REST API (already available from table row)
 * - Snapshot metadata/output: Electric SQL real-time sync via useRepositoryAgentSnapshot
 * - Live progress rows: Electric SQL real-time sync via useRepositoryAgentCodebaseProgress
 * - Event history: Electric SQL on-demand live history per active codebase
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

  const cancelRunMutation = useMutation({
    mutationFn: (payload: {
      ownerName: string;
      repoName: string;
      repositoryWorkflowRunId: string;
    }) =>
      cancelRepositoryAgentRun(
        payload.ownerName,
        payload.repoName,
        payload.repositoryWorkflowRunId,
      ),
    onSuccess: (response, variables) => {
      toast.success(response.message);
      queryClient.invalidateQueries({ queryKey: ["parentWorkflowJobs"] });
      queryClient.invalidateQueries({
        queryKey: [
          "repositoryStatus",
          variables.repoName,
          variables.ownerName,
          variables.repositoryWorkflowRunId,
        ],
      });
      handleDialogOpenChange(false);
    },
    onError: (error: unknown) => {
      toast.error(
        getApiErrorMessage(error, "Failed to cancel AGENTS.md workflow"),
      );
    },
  });

  const createPrMutation = useMutation({
    mutationFn: createRepositoryAgentMdPr,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [
          "repositoryAgentMdPrStatus",
          job?.repository_owner_name,
          job?.repository_name,
          job?.repository_workflow_run_id,
        ],
      });
    },
  });

  // Fresh job lookup from query cache - prevents stale prop issues
  // The job prop is a snapshot from row click; this gets the latest data after invalidation/refetch
  const { data: freshJob } = useQuery<
    ParentWorkflowJobResponse[],
    Error,
    ParentWorkflowJobResponse | undefined
  >({
    queryKey: ["parentWorkflowJobs"],
    queryFn: async (): Promise<ParentWorkflowJobResponse[]> => {
      const response = await getParentWorkflowJobs();
      return response.jobs;
    },
    placeholderData: keepPreviousData,
    staleTime: 1000 * 60 * 1, // Match the source query's stale time
    select: (jobs) =>
      jobs.find(
        (j) => j.repository_workflow_run_id === job?.repository_workflow_run_id,
      ),
    enabled: open && !!job,
  });

  // Use fresh data from cache when available, fallback to prop for initial render
  const actualJob = freshJob ?? job;

  // Build scope for Electric SQL query - requires runId from job
  const scope = job
    ? {
        owner: job.repository_owner_name,
        repository: job.repository_name,
        runId: job.repository_workflow_run_id,
      }
    : null;

  // Electric SQL hook for real-time progress data
  const {
    parsedSnapshot,
    isLoading: isLiveLoading,
    isError: isLiveError,
    isReady: isLiveReady,
    status: snapshotLiveStatus,
    collection,
  } = useRepositoryAgentSnapshot(open ? scope : null);
  const {
    progressRows,
    codebases: liveCodebases,
    isLoading: isProgressLoading,
    isError: isProgressError,
    collection: progressCollection,
  } = useRepositoryAgentCodebaseProgress(open ? scope : null);

  React.useEffect(() => {
    if (open) {
      return undefined;
    }

    const timeoutId = setTimeout(() => {
      if (collection) {
        void collection.cleanup();
      }
      if (progressCollection) {
        void progressCollection.cleanup();
      }
    }, 500);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [open, collection, progressCollection]);

  const codebaseIds = liveCodebases.map((codebase) => codebase.codebaseName);
  const isAnyLiveError = isLiveError || isProgressError;
  const liveStatus = isProgressError ? "progress error" : snapshotLiveStatus;

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

  // Derive status from actualJob (fresh cache data or prop fallback)
  const jobStatus = actualJob?.status ?? "SUBMITTED";
  const isRunning = isInFlightJobStatus(jobStatus);
  const isCompleted = jobStatus === "COMPLETED";
  // ERROR = partial failure (some agents succeeded, some failed)
  const isFailed = jobStatus === "FAILED" || jobStatus === "ERROR";
  const isCancelled = jobStatus === "CANCELLED";
  const canCancelWorkflow =
    !!actualJob &&
    isAgentWorkflowOperation(actualJob.operation) &&
    isRunning &&
    (actualJob.is_cancellable ?? true);

  // Persisted PR status — query when dialog open + job completed
  const { data: persistedPrStatus } =
    useQuery<RepositoryAgentMdPrStatusResponse>({
      queryKey: [
        "repositoryAgentMdPrStatus",
        job?.repository_owner_name,
        job?.repository_name,
        job?.repository_workflow_run_id,
      ],
      queryFn: () => {
        if (!job) {
          return { exists: false, pr_metadata: null };
        }
        return getRepositoryAgentMdPrStatus(
          job.repository_owner_name,
          job.repository_name,
          job.repository_workflow_run_id,
        );
      },
      enabled: open && isCompleted && !!job,
      staleTime: 30_000,
    });

  const persistedPrResult = persistedPrStatus?.exists
    ? persistedPrStatus.pr_metadata
    : null;

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
            .filter(
              (run: WorkflowRun) =>
                run.status === "FAILED" || run.status === "ERROR",
            )
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
    const isErrorState =
      repositoryStatus.status === "FAILED" ||
      repositoryStatus.status === "ERROR";
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
  }, [
    repositoryStatus?.issue_tracking?.issue_url,
    hasReportableRepositoryError,
    failedCodebaseRuns,
  ]);

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

  const handleCreateOrUpdatePr = (): void => {
    if (!actualJob || createPrMutation.isPending || persistedPrResult) {
      return;
    }

    createPrMutation.mutate({
      owner_name: actualJob.repository_owner_name,
      repo_name: actualJob.repository_name,
      repository_workflow_run_id: actualJob.repository_workflow_run_id,
    });
  };

  const handleCancelWorkflow = (): void => {
    if (!actualJob || cancelRunMutation.isPending || !canCancelWorkflow) {
      return;
    }

    cancelRunMutation.mutate({
      ownerName: actualJob.repository_owner_name,
      repoName: actualJob.repository_name,
      repositoryWorkflowRunId: actualJob.repository_workflow_run_id,
    });
  };

  const handleDialogOpenChange = (nextOpen: boolean): void => {
    if (!nextOpen) {
      createPrMutation.reset();
      cancelRunMutation.reset();
    }
    onOpenChange(nextOpen);
  };

  const prResult = createPrMutation.data ?? persistedPrResult;
  const prErrorMessage = createPrMutation.isError
    ? getApiErrorMessage(createPrMutation.error, "Failed to publish PR")
    : null;

  if (!job) {
    return null;
  }

  return (
    <>
      <Dialog open={open} onOpenChange={handleDialogOpenChange}>
        <DialogContent className="flex max-h-[85vh] flex-col p-6 sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>AGENTS.md</DialogTitle>
            <DialogDescription>
              Track generation progress, preview results, and view usage
              statistics.
            </DialogDescription>
          </DialogHeader>

          {/* Section: Run Details */}
          <div className="mt-1 flex justify-center">
            <Badge variant="section">Run Details</Badge>
          </div>

          <Card className="space-y-3 p-4">
            <div>
              <div className="text-muted-foreground text-xs tracking-wide uppercase">
                Repository
              </div>
              <div className="text-sm font-medium">
                {job.repository_owner_name}/{job.repository_name}
              </div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs tracking-wide uppercase">
                Run ID
              </div>
              <div className="text-muted-foreground font-mono text-xs">
                {job.repository_workflow_run_id}
              </div>
            </div>
          </Card>

          {/* Main Content Area — tabbed when statistics available, flat otherwise */}
          {showStatistics && parsedSnapshot?.statistics ? (
            <Tabs
              defaultValue="progress"
              className="flex min-h-0 flex-1 flex-col"
            >
              <TabsList className="mt-1 w-fit self-center">
                <TabsTrigger value="progress">Progress</TabsTrigger>
                <TabsTrigger value="statistics">Statistics</TabsTrigger>
              </TabsList>

              <TabsContent
                value="progress"
                className="flex min-h-0 flex-1 flex-col overflow-y-auto"
              >
                {/* Loading State */}
                {isLiveLoading && !isLiveReady && (
                  <div className="text-sm">
                    Connecting to real-time updates...
                  </div>
                )}

                {/* Error State */}
                {isAnyLiveError && (
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

                            if (progressCollection) {
                              await progressCollection.cleanup();
                              if (progressCollection.utils.clearError) {
                                progressCollection.utils.clearError();
                              }
                              await progressCollection.preload();
                            }
                          };

                          void restart();
                        }}
                      >
                        Retry Sync
                      </Button>
                      <div className="text-muted-foreground text-xs">
                        Status:{" "}
                        {isProgressError ? "progress error" : liveStatus}
                      </div>
                    </div>
                  </div>
                )}

                {/* Progress Display - shown when we have codebaseIds */}
                {codebaseIds.length > 0 && scope && (
                  <GenerateAgentsProgressLive
                    snapshot={parsedSnapshot}
                    scope={scope}
                    progressRows={progressRows}
                    isSyncing={isLiveLoading || isProgressLoading || isRunning}
                  />
                )}

                {/* Waiting for data state */}
                {!isAnyLiveError && codebaseIds.length === 0 && isRunning && (
                  <div className="text-muted-foreground py-8 text-center">
                    <p>Waiting for workflow to start...</p>
                    <p className="mt-2 text-sm">
                      Real-time updates will appear automatically.
                    </p>
                  </div>
                )}
              </TabsContent>

              <TabsContent
                value="statistics"
                className="flex min-h-0 flex-1 flex-col overflow-y-auto"
              >
                <AgentStatisticsDisplay
                  statistics={parsedSnapshot.statistics}
                />
              </TabsContent>
            </Tabs>
          ) : (
            <>
              {/* Section: Progress (no tabs when statistics unavailable) */}
              <div className="mt-1 flex justify-center">
                <Badge variant="section">Progress</Badge>
              </div>

              <div className="flex min-h-0 flex-1 flex-col overflow-y-auto">
                {/* Loading State */}
                {isLiveLoading && !isLiveReady && (
                  <div className="text-sm">
                    Connecting to real-time updates...
                  </div>
                )}

                {/* Error State */}
                {isAnyLiveError && (
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

                            if (progressCollection) {
                              await progressCollection.cleanup();
                              if (progressCollection.utils.clearError) {
                                progressCollection.utils.clearError();
                              }
                              await progressCollection.preload();
                            }
                          };

                          void restart();
                        }}
                      >
                        Retry Sync
                      </Button>
                      <div className="text-muted-foreground text-xs">
                        Status:{" "}
                        {isProgressError ? "progress error" : liveStatus}
                      </div>
                    </div>
                  </div>
                )}

                {/* Progress Display - shown when we have codebaseIds */}
                {codebaseIds.length > 0 && scope && (
                  <GenerateAgentsProgressLive
                    snapshot={parsedSnapshot}
                    scope={scope}
                    progressRows={progressRows}
                    isSyncing={isLiveLoading || isProgressLoading || isRunning}
                  />
                )}

                {/* Waiting for data state */}
                {!isAnyLiveError && codebaseIds.length === 0 && isRunning && (
                  <div className="text-muted-foreground py-8 text-center">
                    <p>Waiting for workflow to start...</p>
                    <p className="mt-2 text-sm">
                      Real-time updates will appear automatically.
                    </p>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Footer Actions */}
          <div className="mt-1 flex items-center justify-between gap-3">
            {/* Left side: Status + Actions based on job state */}
            {isFailed ? (
              <ButtonGroup>
                <Badge
                  variant="failed"
                  className="border-destructive/30 gap-1 rounded-md"
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
              <div className="flex flex-col gap-2">
                <ButtonGroup>
                  {/* Completed state: Show Give Feedback or Track Feedback button */}
                  {/* Use actualJob for fresh feedback_issue_url data from cache */}
                  {actualJob?.feedback_issue_url ? (
                    <Button size="sm" variant="outline" asChild>
                      <a
                        href={actualJob.feedback_issue_url}
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
                  )}

                  {prResult?.pr_url ? (
                    <Button size="sm" variant="outline" asChild>
                      <a
                        href={prResult.pr_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <ExternalLink className="mr-1.5 h-3 w-3" />
                        Open PR
                      </a>
                    </Button>
                  ) : prResult ? (
                    <Button size="sm" variant="outline" disabled>
                      No Changes
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCreateOrUpdatePr}
                      disabled={createPrMutation.isPending}
                    >
                      {createPrMutation.isPending
                        ? "Publishing PR..."
                        : "Publish PR"}
                    </Button>
                  )}
                </ButtonGroup>

                {(createPrMutation.isError || prResult) && (
                  <div className="text-muted-foreground text-xs">
                    {prErrorMessage ?? prResult?.message}
                  </div>
                )}
              </div>
            ) : isRunning ? (
              <ButtonGroup>
                <Badge variant="running" className="gap-1 rounded-md">
                  In Progress
                </Badge>
                {canCancelWorkflow && (
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={handleCancelWorkflow}
                    disabled={cancelRunMutation.isPending}
                  >
                    {cancelRunMutation.isPending
                      ? "Requesting cancel..."
                      : "Cancel Run"}
                  </Button>
                )}
              </ButtonGroup>
            ) : isCancelled ? (
              <ButtonGroup>
                <Badge variant="cancelled" className="gap-1 rounded-md">
                  <XCircle className="h-3 w-3" />
                  Cancelled
                </Badge>
              </ButtonGroup>
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
      {liveCodebases.length > 0 && actualJob && (
        <AgentFeedbackSheet
          open={agentFeedbackSheetOpen}
          onOpenChange={setAgentFeedbackSheetOpen}
          job={actualJob}
          codebases={liveCodebases}
        />
      )}
    </>
  );
}
