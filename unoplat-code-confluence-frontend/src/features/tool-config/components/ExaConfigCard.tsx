import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  Settings,
  Trash2,
  ExternalLink,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { ExaConfigForm } from "./ExaConfigForm";
import { useToolConfig } from "@/hooks/useToolConfig";
import { useDeleteToolConfig } from "@/hooks/useSaveToolConfig";
import {
  TOOL_PROVIDER_DISPLAY_NAMES,
  TOOL_PROVIDER_DESCRIPTIONS,
  TOOL_PROVIDER_HELP_URLS,
} from "../constants";
import { cn } from "@/lib/utils";

interface ExaConfigCardProps {
  className?: string;
}

/**
 * Card component for displaying and managing Exa tool configuration
 * Shows configuration status, provides edit/delete functionality
 */
export function ExaConfigCard({
  className,
}: ExaConfigCardProps): React.ReactElement {
  const [isEditing, setIsEditing] = React.useState(false);
  const { data: config, isLoading, error, refetch } = useToolConfig("exa");
  const deleteConfigMutation = useDeleteToolConfig();

  const isConfigured = config?.status === "configured";

  const errorMessage = error
    ? error instanceof Error
      ? error.message
      : "Failed to load configuration"
    : null;

  const handleRetry = () => {
    refetch();
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleSuccess = () => {
    setIsEditing(false);
    refetch();
  };

  const handleDelete = () => {
    deleteConfigMutation.mutate(
      { provider: "exa" },
      {
        onSuccess: () => {
          refetch();
        },
      },
    );
  };

  const formatTimestamp = (timestamp: string | null | undefined): string => {
    if (!timestamp) return "";
    try {
      return new Date(timestamp).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return timestamp;
    }
  };

  if (isLoading) {
    return (
      <Card className={cn("border-border bg-card", className)}>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="text-muted-foreground h-6 w-6 animate-spin" />
        </CardContent>
      </Card>
    );
  }

  if (errorMessage) {
    return (
      <Card className={cn("border-border bg-card", className)}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="text-lg font-semibold">
                {TOOL_PROVIDER_DISPLAY_NAMES.exa}
              </CardTitle>
              <CardDescription className="text-muted-foreground text-sm">
                {TOOL_PROVIDER_DESCRIPTIONS.exa}
              </CardDescription>
            </div>
            <a
              href={TOOL_PROVIDER_HELP_URLS.exa}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground transition-colors"
              aria-label="View Exa documentation"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span className="text-xs">Failed to load configuration</span>
              <Button variant="outline" size="sm" onClick={handleRetry}>
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("border-border bg-card", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <CardTitle className="text-lg font-semibold">
                {TOOL_PROVIDER_DISPLAY_NAMES.exa}
              </CardTitle>
              <Badge
                variant={isConfigured ? "completed" : "pending"}
                className="text-xs"
              >
                {isConfigured ? "Configured" : "Not Configured"}
              </Badge>
            </div>
            <CardDescription className="text-muted-foreground text-sm">
              {TOOL_PROVIDER_DESCRIPTIONS.exa}
            </CardDescription>
          </div>

          <a
            href={TOOL_PROVIDER_HELP_URLS.exa}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
            aria-label="View Exa documentation"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {isConfigured && config?.configured_at && !isEditing && (
          <p className="text-muted-foreground text-xs">
            Configured on {formatTimestamp(config.configured_at)}
          </p>
        )}

        {isEditing ? (
          <ExaConfigForm
            onCancel={handleCancelEdit}
            onSuccess={handleSuccess}
          />
        ) : (
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleEdit}>
              <Settings className="mr-2 h-4 w-4" />
              {isConfigured ? "Update" : "Configure"}
            </Button>

            {isConfigured && (
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-destructive hover:bg-destructive/10 hover:text-destructive"
                    disabled={deleteConfigMutation.isPending}
                  >
                    {deleteConfigMutation.isPending ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="mr-2 h-4 w-4" />
                    )}
                    Delete
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>
                      Delete Exa Configuration?
                    </AlertDialogTitle>
                    <AlertDialogDescription>
                      This will permanently delete your Exa API key. You will
                      need to reconfigure it to use Exa search features.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={handleDelete}
                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    >
                      Delete
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
