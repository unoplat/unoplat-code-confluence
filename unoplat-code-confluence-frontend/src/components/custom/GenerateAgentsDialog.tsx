import React from 'react';
import { useQuery } from '@tanstack/react-query';
import type { IngestedRepository, CodebaseMetadataResponse } from '@/types';
import { getCodebaseMetadata, getRepositoryAgentSnapshot } from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Card } from '@/components/ui/card';
import { useAgentGenerationStore } from '@/stores/useAgentGenerationStore';
import { GenerateAgentsProgress } from '@/components/custom/GenerateAgentsProgress';
import { Button } from '@/components/ui/button';
import { GenerateAgentsPreview } from '@/components/custom/GenerateAgentsPreview';
import { codebasesToMarkdown } from '@/lib/agent-md-to-markdown';

interface GenerateAgentsDialogProps {
  repository: IngestedRepository | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function GenerateAgentsDialog({ repository, open, onOpenChange }: GenerateAgentsDialogProps): React.ReactElement | null {
  const connect = useAgentGenerationStore((s) => s.connect);
  const parsedCodebases = useAgentGenerationStore((s) => s.parsedCodebases);
  const hasExistingSnapshot = useAgentGenerationStore((s) => s.hasExistingSnapshot);
  const loadExistingSnapshot = useAgentGenerationStore((s) => s.loadExistingSnapshot);
  const startRerun = useAgentGenerationStore((s) => s.startRerun);
  const reset = useAgentGenerationStore((s) => s.reset);

  const [isPreviewOpen, setIsPreviewOpen] = React.useState<boolean>(false);
  const [isCheckingExisting, setIsCheckingExisting] = React.useState<boolean>(false);
  const [shouldConnect, setShouldConnect] = React.useState<boolean>(false);

  const { data, isLoading } = useQuery<CodebaseMetadataResponse>({
    enabled: open && !!repository,
    queryKey: ['codebase-metadata', repository?.repository_owner_name, repository?.repository_name],
    queryFn: () =>
      getCodebaseMetadata(
        repository!.repository_owner_name,
        repository!.repository_name
      ),
    staleTime: 60_000,
  });

  // Check for existing agents.md when dialog opens
  React.useEffect(() => {
    if (!open || !repository) {
      return;
    }

    let isActive = true;

    setIsCheckingExisting(true);
    setShouldConnect(false);

    // Check for existing snapshot
    getRepositoryAgentSnapshot(
      repository.repository_owner_name,
      repository.repository_name
    )
      .then((snapshot) => {
        if (!isActive) {
          return;
        }

        if (snapshot) {
          // Load existing snapshot
          loadExistingSnapshot(snapshot);
          setShouldConnect(false);
        } else {
          // No existing snapshot, should connect
          setShouldConnect(true);
        }
      })
      .catch((error) => {
        if (!isActive) {
          return;
        }

        console.error('Failed to check existing snapshot:', error);
        // On error, proceed with connection
        setShouldConnect(true);
      })
      .finally(() => {
        if (isActive) {
          setIsCheckingExisting(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [open, repository, loadExistingSnapshot]);

  // Connect to SSE only when shouldConnect is true
  React.useEffect(() => {
    if (shouldConnect && repository && data?.codebases?.length) {
      const ids = data.codebases.map((c) => c.codebase_folder);
      connect(repository.repository_owner_name, repository.repository_name, ids);
    }
  }, [shouldConnect, repository, data, connect]);

  // Reset state when dialog closes
  React.useEffect(() => {
    if (!open) {
      reset();
      setShouldConnect(false);
      setIsCheckingExisting(false);
    }
  }, [open, reset]);

  const handleRerun = (): void => {
    if (repository && data?.codebases?.length) {
      startRerun();
      setShouldConnect(true);
    }
  };

  if (!repository) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl max-h-[85vh] flex flex-col" padding="default">
        <DialogHeader>
          <DialogTitle>Generate Agents.md</DialogTitle>
          <DialogDescription>
            Generate precise metadata for your repository's AI agents and workflows.
          </DialogDescription>
        </DialogHeader>
        <Card className="p-4">
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Repository</div>
            <div className="text-sm font-medium">
              {repository.repository_name}
            </div>
          </div>
        </Card>
        <div className="mt-4 flex-1 min-h-0 flex flex-col">
          {isCheckingExisting && (
            <div className="text-sm">Checking for existing agents.md output...</div>
          )}

          {!isCheckingExisting && hasExistingSnapshot && !shouldConnect && (
            <div className="space-y-4">
              <div className="text-sm text-green-600">
                ✓ Agents.md already present
              </div>
              <div className="text-sm text-muted-foreground">
                You can preview the existing result or re-run the generation.
              </div>
            </div>
          )}

          {!isCheckingExisting && !hasExistingSnapshot && isLoading && (
            <div className="text-sm">Detecting codebases...</div>
          )}

          {!isCheckingExisting && !hasExistingSnapshot && !isLoading && (!data?.codebases || data.codebases.length === 0) && (
            <div className="text-sm">No codebases detected.</div>
          )}

          {!isCheckingExisting && shouldConnect && data?.codebases?.length ? (
            <GenerateAgentsProgress
              repository={repository}
              codebaseIds={data.codebases.map((c) => c.codebase_folder)}
            />
          ) : null}
        </div>

        <div className="mt-4 flex items-center justify-end gap-2">
          {hasExistingSnapshot && !shouldConnect && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleRerun}
            >
              Re-run Operation
            </Button>
          )}

          <Button
            size="sm"
            disabled={!parsedCodebases}
            onClick={() => setIsPreviewOpen(true)}
          >
            Preview Result
          </Button>
        </div>

        {parsedCodebases ? (
          <GenerateAgentsPreview
            content={codebasesToMarkdown(parsedCodebases, { title: `AGENTS.md - ${repository.repository_owner_name}/${repository.repository_name}` })}
            fileName="AGENTS.md"
            open={isPreviewOpen}
            onOpenChange={setIsPreviewOpen}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

