import React, { useMemo, useState } from "react";
import { useQueryClient, useMutation } from "@tanstack/react-query";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Github, Trash2 } from "lucide-react";
import { deleteGitHubToken } from "../lib/api";
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
import type { ApiResponse } from "../lib/api"; // Import ApiResponse type
import { DEFAULT_REPOSITORY_CREDENTIAL_PARAMS } from "@/lib/constants/credentials";
import { ProviderKey } from "@/types/credential-enums";
import { useProviderStore } from "@/stores/providerStore";
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
  const providers = useProviderStore((s) => s.providers);
  const removeProvider = useProviderStore((s) => s.removeProvider);
  const [selectedProvider, setSelectedProvider] = useState<ProviderKey | null>(
    providers[0]?.provider_key ?? null,
  );
  const providerOptions = useMemo(
    () => providers.map((p) => p.provider_key as ProviderKey),
    [providers],
  );
  // const [isDeleting, setIsDeleting] = useState<boolean>(false); // Removed isDeleting state
  const queryClient = useQueryClient();
  const { tokenQuery } = useAuthData(); // Use the auth data hook

  // console.log('[SettingsPage] State:', { showTokenPopup, showDeleteDialog });
  // console.log('[SettingsPage] Auth Data:', { tokenQuery });

  // Define the mutation for deleting the token
  const deleteMutation = useMutation<ApiResponse, Error>({
    mutationFn: () => {
      if (!selectedProvider) {
        throw new Error("Select a provider to delete");
      }
      return deleteGitHubToken({
        ...DEFAULT_REPOSITORY_CREDENTIAL_PARAMS,
        provider_key: selectedProvider,
      });
    },
    onSuccess: async (data: ApiResponse) => {
      // console.log('[SettingsPage] Token deleted successfully via mutation, invalidating queries', data);
      setShowDeleteDialog(false);

      // Invalidate and refetch the flag status
      await queryClient.invalidateQueries({
        queryKey: ["flags", "isTokenSubmitted"],
      });
      // console.log('[SettingsPage] Queries invalidated via mutation');

      toast.success(
        data.message || "Provider token has been successfully removed",
      );
      if (selectedProvider) {
        removeProvider(selectedProvider);
        setSelectedProvider(
          providers.filter((p) => p.provider_key !== selectedProvider)[0]
            ?.provider_key ?? null,
        );
      }
    },
    onError: (error: Error) => {
      console.error("[SettingsPage] Error deleting token via mutation:", error);
      toast.error(error.message || "Failed to delete token");
    },
    // Optional: Reset mutation state when dialog closes
    // onSettled: () => {
    //   if (!showDeleteDialog) {
    //     deleteMutation.reset();
    //   }
    // }
  });

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
                        {providers.length > 0 ? "Update Token" : "Add Provider"}
                      </span>
                    </Button>
                  }
                  isUpdate={providers.length > 0}
                  existingProvider={
                    selectedProvider ?? providers[0]?.provider_key
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
                    disabled={deleteMutation.isPending || tokenQuery.isLoading} // Use isPending instead of isLoading
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
            deleteMutation.reset(); // Reset mutation state if dialog is closed
          }
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete provider token</AlertDialogTitle>
            <AlertDialogDescription className="space-y-3">
              <div>
                Choose the provider whose token you want to delete. This removes
                access to its repositories and cannot be undone.
              </div>
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
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMutation.isPending}>
              Cancel
            </AlertDialogCancel>{" "}
            {/* Use isPending */}
            <AlertDialogAction
              onClick={(): void => {
                if (!selectedProvider) return;
                deleteMutation.mutate();
              }}
              disabled={deleteMutation.isPending} // Use isPending
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}{" "}
              {/* Use isPending */}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
