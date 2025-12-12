import React from "react";
import type { ParentWorkflowJobResponse } from "@/types";
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
  const isFailed = jobStatus === "FAILED";

  // Show statistics only when completed and data available
  const showStatistics = isCompleted && parsedSnapshot?.statistics;

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

          {/* Failed Job State */}
          {isFailed && (
            <div className="space-y-2">
              <div className="text-sm text-red-600">
                The operation ended with an error.
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
        <div className="mt-6 flex items-center justify-end gap-3">
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
  );
}
