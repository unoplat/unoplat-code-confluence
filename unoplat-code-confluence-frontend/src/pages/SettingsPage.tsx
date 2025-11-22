import React, { useMemo, useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Github, Trash2 } from "lucide-react";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { useAuthData } from "@/hooks/use-auth-data";
import { useProviderData } from "@/hooks/use-provider-data";
import { useProviderMutations } from "@/hooks/use-provider-mutations";
import type { ApiResponse } from "../lib/api"; // Import ApiResponse type
import { DEFAULT_REPOSITORY_CREDENTIAL_PARAMS } from "@/lib/constants/credentials";
import { ProviderKey } from "@/types/credential-enums";
import { RepositoryProviderForm } from "@/components/custom/RepositoryProviderForm";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getProviderDisplayName } from "@/lib/utils/provider-utils";
import { Label } from "@/components/ui/label";

export default function SettingsPage(): React.ReactElement {
  // console.log('[SettingsPage] Rendering SettingsPage component');

  const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false);
  const { data: providers, isPending: isLoadingProviders } = useProviderData();
  const { deleteToken } = useProviderMutations();
  const [selectedProvider, setSelectedProvider] = useState<ProviderKey | null>(
    providers?.[0]?.provider_key ?? null,
  );
  const providerOptions = useMemo(
    () => (providers ?? []).map((p) => p.provider_key as ProviderKey),
    [providers],
  );
  const { tokenQuery } = useAuthData(); // Use the auth data hook

  // console.log('[SettingsPage] State:', { showTokenPopup, showDeleteDialog });
  // console.log('[SettingsPage] Auth Data:', { tokenQuery });

  // Handle delete token with automatic cache invalidation
  const handleDeleteToken = () => {
    if (!selectedProvider) {
      toast.error("Select a provider to delete");
      return;
    }

    deleteToken.mutate(
      {
        ...DEFAULT_REPOSITORY_CREDENTIAL_PARAMS,
        provider_key: selectedProvider,
      },
      {
        onSuccess: (data: ApiResponse) => {
          setShowDeleteDialog(false);
          toast.success(
            data.message || "Provider token has been successfully removed",
          );
          // Update selected provider to next available
          const remainingProviders =
            providers?.filter((p) => p.provider_key !== selectedProvider) ?? [];
          setSelectedProvider(remainingProviders[0]?.provider_key ?? null);
        },
        onError: (error: Error) => {
          console.error(
            "[SettingsPage] Error deleting token via mutation:",
            error,
          );
          toast.error(error.message || "Failed to delete token");
        },
      },
    );
  };

  // Removed handleDeleteToken function

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-6">
        <Card className="border-border bg-card shadow-md">
          <CardHeader className="mx-auto max-w-4xl px-8 py-6">
            <div className="flex items-center justify-between space-x-6">
              <div className="space-y-2">
                <CardTitle className="text-xl font-semibold tracking-tight">
                  GitHub Authentication
                </CardTitle>
                <CardDescription className="text-muted-foreground text-base leading-relaxed">
                  {tokenQuery.data?.status
                    ? "Update or remove your GitHub Personal Access Token."
                    : "Connect your GitHub account to access repositories."}
                </CardDescription>
              </div>
              <div className="flex items-center gap-3">
                <RepositoryProviderForm
                  trigger={
                    <Button
                      variant="outline"
                      size="default"
                      className="flex min-w-[120px] items-center gap-2"
                    >
                      <Github className="h-4 w-4" />
                      <span>
                        {providers && providers.length > 0
                          ? "Update Token"
                          : "Add Provider"}
                      </span>
                    </Button>
                  }
                  isUpdate={(providers ?? []).length > 0}
                  existingProvider={
                    selectedProvider ?? providers?.[0]?.provider_key
                  }
                />
                {providerOptions.length > 0 && (
                  <Button
                    variant="destructive"
                    size="icon"
                    onClick={(): void => {
                      // console.log('[SettingsPage] Opening delete token confirmation dialog');
                      setShowDeleteDialog(true);
                    }}
                    title="Delete GitHub Token"
                    disabled={deleteToken.isPending || tokenQuery.isLoading || isLoadingProviders}
                    className="h-10 w-10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
        </Card>
      </div>
      {/* Delete Token Confirmation Dialog */}
      <AlertDialog
        open={showDeleteDialog}
        onOpenChange={(isOpen: boolean): void => {
          // console.log('[SettingsPage] Delete dialog change:', isOpen);
          setShowDeleteDialog(isOpen);
          if (!isOpen) {
            // console.log('[SettingsPage] Resetting delete mutation state on dialog close');
            deleteToken.reset(); // Reset mutation state if dialog is closed
          }
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete provider token</AlertDialogTitle>
            <div className="space-y-3">
              <AlertDialogDescription>
                Choose the provider whose token you want to delete. This removes
                access to its repositories and cannot be undone.
              </AlertDialogDescription>
              <div>
                <Label className="mb-1 block text-sm font-medium">
                  Provider
                </Label>
                <Select
                  value={selectedProvider ?? undefined}
                  onValueChange={(val) =>
                    setSelectedProvider(val as ProviderKey)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select provider" />
                  </SelectTrigger>
                  <SelectContent>
                    {providerOptions.map((key) => (
                      <SelectItem key={key} value={key}>
                        {getProviderDisplayName(key)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteToken.isPending}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteToken}
              disabled={deleteToken.isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteToken.isPending ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
