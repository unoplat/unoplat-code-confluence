import React from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import type { RepositoryArtifactMetadataState } from "@/features/repository-agent-snapshots/artifact-hooks";
import type { ArtifactPublicationError } from "@/features/repository-agent-snapshots/schema";

interface ArtifactAvailabilityNoticeProps {
  metadata: RepositoryArtifactMetadataState;
}

function PublicationErrorDetail({
  error,
}: {
  error: ArtifactPublicationError;
}): React.ReactElement {
  return (
    <>
      <span className="block">{error.message}</span>
      <code className="mt-1 block text-xs">{error.code}</code>
    </>
  );
}

/**
 * Explains why generated files can or cannot be viewed for the selected run.
 */
export function ArtifactAvailabilityNotice({
  metadata,
}: ArtifactAvailabilityNoticeProps): React.ReactElement | null {
  if (metadata.status === "idle") {
    return null;
  }

  if (metadata.status === "loading") {
    return (
      <output className="text-muted-foreground block text-xs">
        Checking generated files…
      </output>
    );
  }

  if (metadata.status === "error") {
    return (
      <Alert variant="destructive" size="sm">
        <AlertTitle>File status could not be loaded</AlertTitle>
        <AlertDescription>
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="mt-2"
            disabled={metadata.isRetrying}
            onClick={metadata.retry}
          >
            {metadata.isRetrying ? "Retrying…" : "Retry"}
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  const { availability } = metadata;

  switch (availability.availability) {
    case "available":
      return availability.publicationError ? (
        <Alert variant="warning" size="sm">
          <AlertTitle>Files are available, but PR creation failed</AlertTitle>
          <AlertDescription>
            <PublicationErrorDetail error={availability.publicationError} />
          </AlertDescription>
        </Alert>
      ) : null;
    case "pending":
      return null;
    case "no_artifacts":
      return (
        <Alert size="sm">
          <AlertTitle>No generated files</AlertTitle>
          <AlertDescription>
            This run finished without any managed files to view.
          </AlertDescription>
        </Alert>
      );
    case "failed":
      return (
        <Alert variant="destructive" size="sm">
          <AlertTitle>Files were not published</AlertTitle>
          <AlertDescription>
            {availability.publicationError ? (
              <PublicationErrorDetail error={availability.publicationError} />
            ) : (
              "This run did not save a verified Git commit."
            )}
          </AlertDescription>
        </Alert>
      );
    case "unavailable":
      return (
        <Alert size="sm">
          <AlertTitle>Files are unavailable for this run</AlertTitle>
          <AlertDescription>
            This run has no saved Git commit. Run generation again to view its
            files.
          </AlertDescription>
        </Alert>
      );
  }
}
