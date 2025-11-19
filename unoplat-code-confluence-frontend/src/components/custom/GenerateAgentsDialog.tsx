import React from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import type { IngestedRepository, CodebaseMetadataResponse } from "@/types";
import {
  getCodebaseMetadata,
  getRepositoryAgentSnapshot,
  startRepositoryAgentRun,
  type RepositoryAgentSnapshot,
  type RepoAgentSnapshotStatus,
} from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Card } from "@/components/ui/card";
import { GenerateAgentsProgress } from "@/components/custom/GenerateAgentsProgress";
import { Button } from "@/components/ui/button";
import { GenerateAgentsPreview } from "@/components/custom/GenerateAgentsPreview";
import { AgentStatisticsDisplay } from "@/components/custom/AgentStatisticsDisplay";
import { codebasesToMarkdown } from "@/lib/agent-md-to-markdown";
import { useRepositoryAgentSnapshot } from "@/features/repository-agent-snapshots/hooks";
import { parseAgentMdOutputsFromSnapshot } from "@/features/repository-agent-snapshots/transformers";

interface GenerateAgentsDialogProps {
  repository: IngestedRepository | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function GenerateAgentsDialog({
  repository,
  open,
  onOpenChange,
}: GenerateAgentsDialogProps): React.ReactElement | null {
  const [isPreviewOpen, setIsPreviewOpen] = React.useState<boolean>(false);
  const [kickOffErrorMessage, setKickOffErrorMessage] = React.useState<
    string | null
  >(null);

  const { data, isLoading } = useQuery<CodebaseMetadataResponse>({
    enabled: open && !!repository,
    queryKey: [
      "codebase-metadata",
      repository?.repository_owner_name,
      repository?.repository_name,
    ],
    queryFn: () =>
      getCodebaseMetadata(
        repository!.repository_owner_name,
        repository!.repository_name,
      ),
    staleTime: 60_000,
  });

  const {
    data: snapshot,
    isLoading: isSnapshotLoading,
    refetch: refetchSnapshot,
  } = useQuery<RepositoryAgentSnapshot | null>({
    enabled: open && !!repository,
    queryKey: [
      "repository-agent-snapshot",
      repository?.repository_owner_name,
      repository?.repository_name,
    ],
    queryFn: () =>
      getRepositoryAgentSnapshot(
        repository!.repository_owner_name,
        repository!.repository_name,
      ),
    refetchOnWindowFocus: false,
  });
  const scope = repository
    ? {
        owner: repository.repository_owner_name,
        repository: repository.repository_name,
      }
    : null;

  const {
    parsedSnapshot,
    isLoading: isLiveLoading,
    isError: isLiveError,
    isReady: isLiveReady,
    status: liveStatus,
    collection,
  } = useRepositoryAgentSnapshot(scope);

  const startRunMutation = useMutation({
    mutationFn: async () => {
      if (!repository) {
        throw new Error("Repository is required to start agent generation");
      }

      return startRepositoryAgentRun(
        repository.repository_owner_name,
        repository.repository_name,
      );
    },
    onSuccess: () => {
      void refetchSnapshot();
    },
    onError: (error: unknown) => {
      const message =
        error instanceof Error
          ? error.message
          : "Failed to start repository workflow";
      setKickOffErrorMessage(message);
    },
  });

  const startRunMutate = startRunMutation.mutate;
  const startRunIsPending = startRunMutation.isPending;
  const startRunIsSuccess = startRunMutation.isSuccess;

  React.useEffect(() => {
    if (!open || !repository) {
      return;
    }

    if (!data?.codebases?.length) {
      return;
    }

    if (startRunIsPending || startRunIsSuccess) {
      return;
    }

    if (isSnapshotLoading) {
      return;
    }

    if (snapshot === null) {
      startRunMutate();
    }
  }, [
    open,
    repository,
    data?.codebases,
    startRunIsPending,
    startRunIsSuccess,
    isSnapshotLoading,
    snapshot,
    startRunMutate,
  ]);

  const { markdownByCodebase: fallbackMarkdown } = React.useMemo(
    () => parseAgentMdOutputsFromSnapshot(snapshot),
    [snapshot],
  );

  const codebaseIds = React.useMemo(
    () => data?.codebases?.map((c) => c.codebase_folder) ?? [],
    [data?.codebases],
  );

  const snapshotMarkdown = parsedSnapshot?.markdownByCodebase;
  const previewCodebases =
    snapshotMarkdown && Object.keys(snapshotMarkdown).length > 0
      ? snapshotMarkdown
      : Object.keys(fallbackMarkdown).length > 0
        ? fallbackMarkdown
        : null;

  const previewContent = React.useMemo(() => {
    if (!repository || !previewCodebases) {
      return null;
    }
    return codebasesToMarkdown(previewCodebases, {
      title: `AGENTS.md - ${repository.repository_owner_name}/${repository.repository_name}`,
    });
  }, [repository, previewCodebases]);

  if (!repository) {
    return null;
  }

  const isCheckingExisting = isSnapshotLoading && snapshot === undefined;

  const currentStatus: RepoAgentSnapshotStatus | "IDLE" =
    parsedSnapshot?.status ?? snapshot?.status ?? "IDLE";

  const hasExistingSnapshot =
    (parsedSnapshot?.status ?? snapshot?.status) === "COMPLETED";
  const isSnapshotRunning = currentStatus === "RUNNING";
  const isSnapshotError =
    (parsedSnapshot?.status ?? snapshot?.status) === "ERROR";
  const showRerunButton = hasExistingSnapshot || isSnapshotError;
  const rerunLabel =
    isSnapshotError && !hasExistingSnapshot
      ? "Retry Operation"
      : "Re-run Operation";
  const showExistingMessage =
    !isCheckingExisting &&
    !isSnapshotRunning &&
    hasExistingSnapshot &&
    currentStatus === "COMPLETED";

  const showStatistics = hasExistingSnapshot && parsedSnapshot?.statistics;

  const handleRerun = (): void => {
    startRunMutation.mutate();
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="flex max-h-[85vh] flex-col p-6 sm:max-w-2xl"
      >
        <DialogHeader>
          <DialogTitle>Generate Agents.md</DialogTitle>
          <DialogDescription>
            Generate precise metadata for your repository&apos;s AI agents and
            workflows.
          </DialogDescription>
        </DialogHeader>
        <Card className="p-4">
          <div className="space-y-1">
            <div className="text-muted-foreground text-sm">Repository</div>
            <div className="text-sm font-medium">
              {repository.repository_name}
            </div>
          </div>
        </Card>
        <div className="mt-4 flex min-h-0 flex-1 flex-col overflow-y-auto">
          {isCheckingExisting && (
            <div className="text-sm">
              Checking for existing agents.md output...
            </div>
          )}

          {!isCheckingExisting && isSnapshotError && (
            <div className="space-y-2">
              <div className="text-sm text-red-600">
                The previous generation ended with an error.
              </div>
              <div className="text-muted-foreground text-sm">
                Re-run the operation when you are ready.
              </div>
            </div>
          )}

          {!isCheckingExisting &&
            currentStatus !== "RUNNING" &&
            !hasExistingSnapshot &&
            isLoading && <div className="text-sm">Detecting codebases...</div>}

          {!isCheckingExisting &&
            currentStatus !== "RUNNING" &&
            !hasExistingSnapshot &&
            !isLoading &&
            codebaseIds.length === 0 && (
              <div className="text-sm">No codebases detected.</div>
            )}

          {kickOffErrorMessage ? (
            <div className="text-sm text-red-600" role="alert">
              {kickOffErrorMessage}
            </div>
          ) : null}

          {isLiveLoading && !isLiveReady ? (
            <div className="text-sm">Preparing live snapshot...</div>
          ) : null}

          {isLiveError ? (
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
          ) : null}

          {!isCheckingExisting && codebaseIds.length > 0 ? (
            <GenerateAgentsProgress
              repository={repository}
              snapshot={parsedSnapshot}
              codebaseIds={codebaseIds}
              isSyncing={isLiveLoading || isSnapshotRunning}
            />
          ) : null}

          {showStatistics ? (
            <div className="mt-6">
              <AgentStatisticsDisplay statistics={parsedSnapshot.statistics} />
            </div>
          ) : null}
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          {showExistingMessage ? (
            <div
              className="flex items-center gap-2 rounded-md bg-green-50 px-2 py-1 text-sm text-green-600"
              title="You can preview the existing result or re-run the generation."
            >
              <span aria-hidden="true">✓</span>
              <span>Agents.md present</span>
            </div>
          ) : (
            <div className="flex-1" />
          )}

          <div className="flex items-center gap-2">
            {showRerunButton && (
              <Button
                size="sm"
                variant="outline"
                disabled={isSnapshotRunning}
                onClick={handleRerun}
              >
                {rerunLabel}
              </Button>
            )}

            <Button
              size="sm"
              disabled={!previewCodebases || isSnapshotRunning}
              onClick={() => setIsPreviewOpen(true)}
            >
              Preview Result
            </Button>
          </div>
        </div>

        {previewCodebases ? (
          <GenerateAgentsPreview
            codebases={previewCodebases}
            repositoryName={`${repository.repository_owner_name}/${repository.repository_name}`}
            open={isPreviewOpen}
            onOpenChange={setIsPreviewOpen}
            onDownloadAll={handleDownloadAll}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
