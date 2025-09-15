import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { StatusBadge } from '@/components/custom/StatusBadge';
import type { IngestedRepository } from '../../types';

interface RefreshRepositoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  repository: IngestedRepository | null;
}

export function RefreshRepositoryDialog({
  open,
  onOpenChange,
  onConfirm,
  repository,
}: RefreshRepositoryDialogProps): React.ReactElement {
  if (!repository) return <></>;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle asChild>
            <div className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" />
              Refresh Repository
              <StatusBadge status="alpha" size="sm" />
            </div>
          </DialogTitle>
          <DialogDescription asChild>
            <div>
              This will trigger a re-ingestion of the repository. This feature is in <StatusBadge status="alpha" size="sm" className="inline-flex mx-1" />
              and may take some time to complete.
            </div>
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <p className="text-sm font-medium">Repository</p>
            <p className="text-sm text-muted-foreground">
              {repository.repository_owner_name}/{repository.repository_name}
            </p>
          </div>
          <div className="rounded-md bg-muted p-3">
            <div className="text-sm text-muted-foreground">
              <strong>Note:</strong> The refresh process will run in the background.
              You can continue using the application while it processes.
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={onConfirm}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Start Refresh
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}