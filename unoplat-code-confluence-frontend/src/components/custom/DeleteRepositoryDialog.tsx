import React from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Trash2 } from "lucide-react";
import { StatusBadge } from "@/components/custom/StatusBadge";
import type { IngestedRepository } from "../../types";

interface DeleteRepositoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  repository: IngestedRepository | null;
}

export function DeleteRepositoryDialog({
  open,
  onOpenChange,
  onConfirm,
  repository,
}: DeleteRepositoryDialogProps): React.ReactElement {
  if (!repository) return <></>;

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle asChild>
            <div className="flex items-center gap-2">
              <Trash2 className="text-destructive h-4 w-4" />
              Delete Repository
              <StatusBadge status="beta" />
            </div>
          </AlertDialogTitle>
          <AlertDialogDescription asChild>
            <div>
              This action cannot be undone. This will permanently delete the
              ingested repository data from our system.
            </div>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <p className="text-sm font-medium">Repository to delete</p>
            <p className="text-muted-foreground text-sm">
              {repository.repository_owner_name}/{repository.repository_name}
            </p>
          </div>
          <div className="bg-destructive/10 rounded-md p-3">
            <div className="text-destructive text-sm">
              <strong>Warning:</strong> This feature is in{" "}
              <StatusBadge
                status="beta"
                className="mx-1 inline-flex"
              />
              . All associated data including code analysis, dependencies, and
              metadata will be removed.
            </div>
          </div>
        </div>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            Delete Repository
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
