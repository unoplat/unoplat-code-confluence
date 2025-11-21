"use client";

import React, { useState, useMemo } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "../ui/dialog";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { DataTable } from "@/components/data-table/data-table";
import {
  getJobStatusDataTableColumns,
  getStatusIcon,
  getStatusVariant,
} from "./job-status-data-table-columns";
import { getRepositoryStatus } from "../../lib/api";
import { apiToUiErrorReport } from "../../lib/error-utils";
import type {
  ParentWorkflowJobResponse,
  FlattenedCodebaseRun,
  CodebaseStatus,
  WorkflowStatus,
  WorkflowRun,
  GithubRepoStatus,
  ApiErrorReport,
} from "../../types";
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  ColumnFiltersState,
} from "@tanstack/react-table";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { FeedbackDialog } from "./FeedbackDialog";

// Define FeedbackSource type to match the one in FeedbackDialog
type FeedbackSource =
  | { type: "codebase"; data: FlattenedCodebaseRun }
  | { type: "repository"; data: GithubRepoStatus };

interface JobStatusDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  job: ParentWorkflowJobResponse | null;
}

export function JobStatusDialog({
  open,
  onOpenChange,
  job,
}: JobStatusDialogProps): React.ReactElement | null {
  const [statusError, setStatusError] = useState<string | null>(null);
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState<boolean>(false);
  const [feedbackSource, setFeedbackSource] = useState<FeedbackSource | null>(
    null,
  );
  const queryClient = useQueryClient();

  // Fetch repository status when dialog is open and job is available
  const {
    data: repositoryStatus,
    isLoading,
    error,
  } = useQuery({
    queryKey: [
      "repositoryStatus",
      job?.repository_name,
      job?.repository_owner_name,
      job?.repository_workflow_run_id,
    ],
    queryFn: async () => {
      console.log(
        "[Query] JobStatusDialog: fetching repositoryStatus for job:",
        job,
      );
      if (!job) return null;
      try {
        const status = await getRepositoryStatus(
          job.repository_name,
          job.repository_owner_name,
          job.repository_workflow_run_id,
        );
        console.log(
          "[Query] JobStatusDialog: raw getRepositoryStatus response:",
          status,
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
      } catch (err) {
        setStatusError("Failed to fetch repository status. Please try again.");
        console.error("Error fetching repository status:", err);
        return null;
      }
    },
    enabled: open && !!job,
    staleTime: 1000 * 60, // 1 minute
    refetchInterval: 1000 * 10,
  });

  // Transform the nested codebase_status_list into a flat array of FlattenedCodebaseRun objects
  const codebaseRuns = useMemo(() => {
    if (!repositoryStatus?.codebase_status_list?.codebases) return [];

    // Flatten the nested structure into a simple array of FlattenedCodebaseRun objects
    return repositoryStatus.codebase_status_list.codebases.flatMap(
      (codebase: CodebaseStatus) => {
        return codebase.workflows.flatMap((workflow: WorkflowStatus) => {
          return workflow.codebase_workflow_runs.map(
            (run: WorkflowRun): FlattenedCodebaseRun => {
              // Convert API error report to UI error report if present
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
                // Use the new accessor keys that match the column definitions
                codebase_folder: codebase.codebase_folder,
                codebase_workflow_run_id: run.codebase_workflow_run_id,
                codebase_status: run.status,
                codebase_started_at: run.started_at,
                codebase_completed_at: run.completed_at,
                codebase_error_report: uiErrorReport,
                codebase_issue_tracking: run.issue_tracking,
              };
            },
          );
        });
      },
    );
  }, [repositoryStatus]);

  // Check if the repository has a reportable error (failed status with error report)
  const hasReportableRepositoryError = useMemo(() => {
    if (!repositoryStatus) return false;
    // Only show feedback button if status is FAILED, has error report, and doesn't already have issue tracking
    return (
      repositoryStatus.status === "FAILED" &&
      !!repositoryStatus.error_report &&
      !repositoryStatus.issue_tracking?.issue_url
    );
  }, [repositoryStatus]);

  // Determine if we should show the feedback column (only for failed status)
  const showFeedbackColumn = useMemo(() => {
    return codebaseRuns.some((run) => run.codebase_status === "FAILED");
  }, [codebaseRuns]);

  // Handle submit feedback action for codebase
  const handleSubmitFeedback = (run: FlattenedCodebaseRun) => {
    setFeedbackSource({ type: "codebase", data: run });
    setFeedbackDialogOpen(true);
  };

  // Handle repository feedback submission
  const handleSubmitRepositoryFeedback = () => {
    if (repositoryStatus) {
      setFeedbackSource({ type: "repository", data: repositoryStatus });
      setFeedbackDialogOpen(true);
    }
  };

  // Handle feedback submission success
  const handleFeedbackSuccess = () => {
    // Invalidate query to refresh data
    queryClient.invalidateQueries({
      queryKey: [
        "repositoryStatus",
        job?.repository_name,
        job?.repository_owner_name,
        job?.repository_workflow_run_id,
      ],
    });
  };

  // Create table columns
  const columns = useMemo(() => {
    return getJobStatusDataTableColumns({
      showFeedbackColumn,
      onSubmitFeedback: handleSubmitFeedback,
    });
  }, [showFeedbackColumn]);

  // Track filter state for client-side filtering
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  // Create table instance for codebase runs
  const table = useReactTable({
    data: codebaseRuns,
    columns,
    state: {
      columnFilters,
    },
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    initialState: {
      pagination: {
        pageSize: 5, // Default page size
      },
    },
    // type: ignore
    getRowId: (row: FlattenedCodebaseRun): string =>
      row.codebase_workflow_run_id,
  });

  // Determine if the job has failed but doesn't have an error report
  const hasFailedWithoutError = useMemo(() => {
    if (!repositoryStatus) return false;
    return (
      repositoryStatus.status === "FAILED" && !repositoryStatus.error_report
    );
  }, [repositoryStatus]);

  // Determine the effective status to display (success if failed but no error report)
  const effectiveStatus = useMemo(() => {
    if (!repositoryStatus) return null;
    if (hasFailedWithoutError) return "COMPLETED";
    return repositoryStatus.status;
  }, [repositoryStatus, hasFailedWithoutError]);

  if (!job) return null;

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent size="lg" className="max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Repository Status Details</DialogTitle>
            <DialogDescription>
              View detailed status information for repository ingestion and
              processing workflows.
            </DialogDescription>
          </DialogHeader>

          {isLoading ? (
            <div className="flex h-40 items-center justify-center">
              <div className="border-primary h-10 w-10 animate-spin rounded-full border-b-2" />
            </div>
          ) : error || statusError ? (
            <div className="bg-destructive/10 border-destructive/20 mt-4 rounded border p-3">
              <p className="text-destructive font-semibold">Error:</p>
              <p className="text-destructive/80">
                {statusError || "An error occurred while fetching data."}
              </p>
            </div>
          ) : repositoryStatus ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <p>
                    <strong>Repository:</strong>{" "}
                    {repositoryStatus.repository_owner_name}/
                    {repositoryStatus.repository_name}
                  </p>
                  <p>
                    <strong>Run ID:</strong>{" "}
                    {repositoryStatus.repository_workflow_run_id}
                  </p>
                  <p>
                    <strong>Started:</strong>{" "}
                    {new Date(repositoryStatus.started_at).toLocaleString(
                      undefined,
                      {
                        year: "numeric",
                        month: "2-digit",
                        day: "2-digit",
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                        hour12: false,
                      },
                    )}
                  </p>
                  {repositoryStatus.completed_at && (
                    <p>
                      <strong>Completed:</strong>{" "}
                      {new Date(repositoryStatus.completed_at).toLocaleString(
                        undefined,
                        {
                          year: "numeric",
                          month: "2-digit",
                          day: "2-digit",
                          hour: "2-digit",
                          minute: "2-digit",
                          second: "2-digit",
                          hour12: false,
                        },
                      )}
                    </p>
                  )}
                </div>
                <div>
                  <p>
                    <strong>Status:</strong>
                    <Badge
                      variant={getStatusVariant(effectiveStatus || "SUBMITTED")}
                      className="ml-2 gap-1"
                    >
                      {getStatusIcon(effectiveStatus || "SUBMITTED")}
                      {hasFailedWithoutError
                        ? "COMPLETED"
                        : repositoryStatus.status}
                    </Badge>
                  </p>
                  {repositoryStatus.error_report && (
                    <div className="mt-2">
                      {repositoryStatus.issue_tracking?.issue_url ? (
                        <p className="flex items-center">
                          <strong>GitHub Issue:</strong>
                          <a
                            href={repositoryStatus.issue_tracking.issue_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary ml-2 inline-flex items-center gap-1 hover:underline"
                          >
                            #{repositoryStatus.issue_tracking.issue_number}
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="16"
                              height="16"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            >
                              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                              <polyline points="15 3 21 3 21 9" />
                              <line x1="10" y1="14" x2="21" y2="3" />
                            </svg>
                          </a>
                        </p>
                      ) : (
                        hasReportableRepositoryError && (
                          <Button
                            size="sm"
                            onClick={handleSubmitRepositoryFeedback}
                            className="mt-2"
                          >
                            Submit Repository Feedback
                          </Button>
                        )
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Codebase Runs Table */}
              {codebaseRuns.length > 0 && (
                <div className="mt-6">
                  <h4 className="mb-2 text-lg font-semibold">Codebase Runs</h4>
                  <div className="rounded-md border">
                    <DataTable table={table} actionBar={null}>
                      <DataTableToolbar table={table} />
                    </DataTable>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p>No details available for this job.</p>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              className=""
            >
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Unified Feedback Dialog for both codebase and repository issues */}
      <FeedbackDialog
        open={feedbackDialogOpen}
        onOpenChange={setFeedbackDialogOpen}
        source={feedbackSource}
        onSuccess={handleFeedbackSuccess}
      />
    </>
  );
}
