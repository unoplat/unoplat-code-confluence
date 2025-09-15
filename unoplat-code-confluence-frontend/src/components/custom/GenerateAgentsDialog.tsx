import React from 'react';
import { useQuery } from '@tanstack/react-query';
import type { IngestedRepository, CodebaseMetadataResponse } from '@/types';
import { getCodebaseMetadata } from '@/lib/api';
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
  const [isPreviewOpen, setIsPreviewOpen] = React.useState<boolean>(false);

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

  React.useEffect(() => {
    if (open && repository && data?.codebases?.length) {
      const ids = data.codebases.map((c) => c.codebase_folder);
      connect(repository.repository_owner_name, repository.repository_name, ids);
    }
  }, [open, repository, data, connect]);

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
          {isLoading && (
            <div className="text-sm">Detecting codebases...</div>
          )}
          {!isLoading && (!data?.codebases || data.codebases.length === 0) && (
            <div className="text-sm">No codebases detected.</div>
          )}
          {!isLoading && data?.codebases?.length ? (
            <GenerateAgentsProgress
              repository={repository}
              codebaseIds={data.codebases.map((c) => c.codebase_folder)}
            />
          ) : null}
        </div>

        <div className="mt-4 flex items-center justify-end gap-2">
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


