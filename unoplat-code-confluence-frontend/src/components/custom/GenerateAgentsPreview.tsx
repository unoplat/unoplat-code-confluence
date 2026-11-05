import * as React from "react";
import {
  ChevronRight,
  Copy,
  Download,
  FileCode,
  FileText,
  Folder,
  Network,
  Search,
  X,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { toast } from "sonner";

import { ArtifactMarkdownPreview } from "@/components/custom/ArtifactMarkdownPreview";
import { SvgPreview } from "@/components/custom/SvgPreview";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent } from "@/components/ui/collapsible";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  useRepositoryArtifactFile,
  useRepositoryMarkdownBundleDownload,
  type RepositoryArtifactFileState,
} from "@/features/repository-agent-snapshots/artifact-hooks";
import type { RepositoryAgentSnapshotScope } from "@/features/repository-agent-snapshots/collection";
import type { ArtifactManifestEntry } from "@/features/repository-agent-snapshots/schema";
import { cn } from "@/lib/utils";

interface GenerateAgentsPreviewProps {
  scope: RepositoryAgentSnapshotScope;
  commitSha: string;
  manifest: ArtifactManifestEntry[];
  repositoryName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  generatedAt?: string;
}

interface ArtifactGroup {
  key: string;
  displayName: string;
  artifacts: ArtifactManifestEntry[];
}

type ArtifactKind = ArtifactManifestEntry["kind"];

const shortCommitShaLength = 7;
const markdownBundleFileName = "AGENTS.md";

const artifactKindLabels: Record<ArtifactKind, string> = {
  markdown: "Markdown",
  d2: "D2 source",
  svg: "SVG",
};

const artifactMimeTypes: Record<ArtifactKind, string> = {
  markdown: "text/markdown;charset=utf-8",
  d2: "text/plain;charset=utf-8",
  svg: "image/svg+xml;charset=utf-8",
};

function getArtifactFileName(entry: ArtifactManifestEntry): string {
  return entry.path.split("/").pop() ?? entry.path;
}

function getArtifactGroupKey(entry: ArtifactManifestEntry): string {
  return entry.scope === "repository"
    ? "repository"
    : `codebase:${entry.codebase_name ?? ""}`;
}

function getArtifactGroupName(entry: ArtifactManifestEntry): string {
  if (entry.scope === "repository") {
    return "Repository";
  }
  return entry.codebase_name === "." ? "Root" : (entry.codebase_name ?? "");
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

function buildArtifactGroups(
  manifest: ArtifactManifestEntry[],
  searchQuery: string,
): ArtifactGroup[] {
  const query = searchQuery.trim().toLocaleLowerCase();
  const groups = new Map<string, ArtifactGroup>();

  for (const entry of manifest) {
    const displayName = getArtifactGroupName(entry);
    const isMatch =
      displayName.toLocaleLowerCase().includes(query) ||
      entry.path.toLocaleLowerCase().includes(query);
    if (!isMatch) {
      continue;
    }

    const key = getArtifactGroupKey(entry);
    const group = groups.get(key);
    if (group) {
      group.artifacts.push(entry);
    } else {
      groups.set(key, { key, displayName, artifacts: [entry] });
    }
  }

  return [...groups.values()];
}

function downloadTextFile(
  fileName: string,
  content: string,
  mimeType: string,
): void {
  const url = URL.createObjectURL(new Blob([content], { type: mimeType }));
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function ArtifactKindIcon({
  kind,
  className,
}: {
  kind: ArtifactKind;
  className?: string;
}): React.ReactElement {
  if (kind === "svg") {
    return <Network className={className} />;
  }
  if (kind === "d2") {
    return <FileCode className={className} />;
  }
  return <FileText className={className} />;
}

function ArtifactContent({
  entry,
  file,
}: {
  entry: ArtifactManifestEntry;
  file: RepositoryArtifactFileState;
}): React.ReactElement | null {
  if (file.status === "idle") {
    return null;
  }

  if (file.status === "loading") {
    return (
      <output className="text-muted-foreground flex h-full items-center justify-center text-sm">
        Loading file from the saved commit…
      </output>
    );
  }

  if (file.status === "error") {
    return (
      <div
        className="flex h-full flex-col items-center justify-center gap-2 p-6 text-center"
        role="alert"
      >
        <p className="text-destructive text-sm">{file.failure.message}</p>
        <code className="text-muted-foreground text-xs">
          {file.failure.code}
        </code>
        {file.failure.retryable && (
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={file.isRetrying}
            onClick={file.retry}
          >
            {file.isRetrying ? "Retrying…" : "Retry"}
          </Button>
        )}
      </div>
    );
  }

  if (entry.kind === "svg") {
    return (
      <SvgPreview
        key={entry.path}
        source={file.content}
        fileName={getArtifactFileName(entry)}
      />
    );
  }

  return (
    <ScrollArea className="bg-muted h-full p-4" viewportClassName="pr-3">
      <div className="border-border bg-card mx-auto min-h-full max-w-3xl rounded-lg border p-5 shadow-sm">
        {entry.kind === "markdown" ? (
          <ArtifactMarkdownPreview markdown={file.content} />
        ) : (
          <pre className="font-mono text-xs break-all whitespace-pre-wrap">
            {file.content}
          </pre>
        )}
      </div>
    </ScrollArea>
  );
}

export function GenerateAgentsPreview({
  scope,
  commitSha,
  manifest,
  repositoryName,
  open,
  onOpenChange,
  generatedAt,
}: GenerateAgentsPreviewProps): React.ReactElement {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedPath, setSelectedPath] = React.useState<string | null>(null);
  const [toggledGroups, setToggledGroups] = React.useState<
    Record<string, boolean>
  >({});

  const defaultArtifact =
    manifest.find((entry) => entry.kind === "svg") ?? manifest[0];
  const selectedArtifact =
    manifest.find((entry) => entry.path === selectedPath) ?? defaultArtifact;
  const defaultGroupKey = selectedArtifact
    ? getArtifactGroupKey(selectedArtifact)
    : null;

  const file = useRepositoryArtifactFile({
    scope,
    commitSha,
    path: selectedArtifact?.path ?? null,
    enabled: open,
  });
  const loadedContent = file.status === "ready" ? file.content : null;
  const markdownBundle = useRepositoryMarkdownBundleDownload({
    scope,
    commitSha,
    repositoryName,
    manifest,
    isActive: open,
    onReady: (markdown) => {
      downloadTextFile(
        markdownBundleFileName,
        markdown,
        artifactMimeTypes.markdown,
      );
    },
    onFailure: (failure) => {
      toast.error(
        `Nothing was downloaded: ${failure.message} (${failure.code})`,
      );
    },
  });

  const groups = React.useMemo(
    () => buildArtifactGroups(manifest, searchQuery),
    [manifest, searchQuery],
  );
  const totalGroupCount = React.useMemo(
    () => new Set(manifest.map(getArtifactGroupKey)).size,
    [manifest],
  );

  const handleCopy = async (): Promise<void> => {
    if (!selectedArtifact || loadedContent === null) {
      return;
    }
    await navigator.clipboard.writeText(loadedContent);
    toast.success(
      `${getArtifactFileName(selectedArtifact)} copied to clipboard`,
    );
  };

  const generatedLabel = React.useMemo(() => {
    if (!generatedAt) return null;
    const generatedDate = new Date(generatedAt);
    if (Number.isNaN(generatedDate.getTime())) return null;
    return `Generated ${formatDistanceToNow(generatedDate, { addSuffix: true })}`;
  }, [generatedAt]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        size="full"
        padding="none"
        gap="none"
        showCloseButton={false}
        aria-describedby="generated-artifacts-description"
        className="flex h-[min(784px,calc(100vh-2rem))] max-h-[calc(100vh-2rem)] w-[min(1160px,calc(100vw-2rem))] flex-col overflow-hidden rounded-xl sm:max-w-[min(1160px,calc(100vw-2rem))]"
      >
        <DialogHeader className="border-border flex h-[72px] shrink-0 flex-row items-center justify-between gap-4 border-b px-5 text-left">
          <div className="min-w-0">
            <DialogTitle className="text-lg">Generated artifacts</DialogTitle>
            <DialogDescription
              id="generated-artifacts-description"
              className="mt-1 text-xs"
            >
              {manifest.length}{" "}
              {manifest.length === 1 ? "artifact" : "artifacts"} across{" "}
              {totalGroupCount} {totalGroupCount === 1 ? "group" : "groups"}
              <span className="sr-only"> for {repositoryName}</span>
            </DialogDescription>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            {markdownBundle.hasMarkdownFiles && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={markdownBundle.isPreparing}
                onClick={markdownBundle.start}
              >
                <Download />
                <span className="hidden sm:inline">
                  {markdownBundle.isPreparing
                    ? "Preparing download…"
                    : "Download all Markdown"}
                </span>
              </Button>
            )}
            <DialogClose asChild>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="size-9"
                aria-label="Close artifact viewer"
              >
                <X />
              </Button>
            </DialogClose>
          </div>
        </DialogHeader>

        <ResizablePanelGroup direction="horizontal" className="min-h-0 flex-1">
          <ResizablePanel defaultSize="24%" minSize="18%" maxSize="38%">
            <aside className="bg-background flex h-full min-w-0 flex-col px-3 py-4">
              <div className="relative shrink-0">
                <Search className="text-muted-foreground pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2" />
                <Input
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  placeholder="Find a codebase or artifact"
                  aria-label="Find a codebase or artifact"
                  className="h-9 pl-9 text-xs"
                />
              </div>

              <div className="text-muted-foreground px-2 pt-3 pb-2 text-[11px] font-semibold tracking-[0.06em] uppercase">
                Files · {groups.length}{" "}
                {groups.length === 1 ? "group" : "groups"}
              </div>

              <ScrollArea className="min-h-0 flex-1" viewportClassName="pr-1">
                {groups.length > 0 ? (
                  <div className="space-y-0.5">
                    {groups.map((group) => {
                      const isOpen =
                        toggledGroups[group.key] ??
                        group.key === defaultGroupKey;
                      return (
                        <Collapsible key={group.key} open={isOpen}>
                          <button
                            type="button"
                            onClick={() => {
                              setToggledGroups((current) => ({
                                ...current,
                                [group.key]: !isOpen,
                              }));
                            }}
                            className="hover:bg-accent focus-visible:ring-ring flex h-12 w-full items-center gap-2 rounded-md px-2 text-left outline-none focus-visible:ring-2"
                            aria-expanded={isOpen}
                          >
                            <Folder className="size-4 shrink-0" />
                            <span className="min-w-0 flex-1">
                              <span className="block truncate text-xs font-semibold">
                                {group.displayName}
                              </span>
                              <span className="text-muted-foreground block truncate text-[11px]">
                                {group.artifacts.length}{" "}
                                {group.artifacts.length === 1
                                  ? "artifact"
                                  : "artifacts"}
                              </span>
                            </span>
                            <ChevronRight
                              className={cn(
                                "text-muted-foreground size-4 shrink-0 transition-transform",
                                isOpen && "rotate-90",
                              )}
                            />
                          </button>

                          <CollapsibleContent>
                            <div className="space-y-0.5 pb-1">
                              {group.artifacts.map((artifact) => {
                                const isSelected =
                                  artifact.path === selectedArtifact?.path;
                                return (
                                  <button
                                    key={artifact.path}
                                    type="button"
                                    onClick={() =>
                                      setSelectedPath(artifact.path)
                                    }
                                    className={cn(
                                      "focus-visible:ring-ring flex min-h-10 w-full items-center gap-2 rounded-md py-1.5 pr-2 pl-9 text-left outline-none focus-visible:ring-2",
                                      isSelected
                                        ? "bg-accent text-accent-foreground"
                                        : "hover:bg-accent/60",
                                    )}
                                    aria-current={
                                      isSelected ? "true" : undefined
                                    }
                                  >
                                    <span className="bg-card border-border flex size-6 shrink-0 items-center justify-center rounded-md border">
                                      <ArtifactKindIcon
                                        kind={artifact.kind}
                                        className="size-3.5"
                                      />
                                    </span>
                                    <span className="min-w-0 flex-1">
                                      <span className="block truncate font-mono text-[11px] font-medium">
                                        {getArtifactFileName(artifact)}
                                      </span>
                                      <span className="text-muted-foreground block truncate text-[10px]">
                                        {artifactKindLabels[artifact.kind]} ·{" "}
                                        {formatBytes(artifact.byte_length)}
                                      </span>
                                    </span>
                                    {isSelected && (
                                      <span className="bg-success size-1.5 shrink-0 rounded-full" />
                                    )}
                                  </button>
                                );
                              })}
                            </div>
                          </CollapsibleContent>
                        </Collapsible>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-muted-foreground px-3 py-8 text-center text-xs">
                    No artifacts match “{searchQuery}”.
                  </div>
                )}
              </ScrollArea>

              <div className="border-border text-muted-foreground mt-3 shrink-0 border-t px-2 pt-3 text-[11px]">
                {generatedLabel && <div>{generatedLabel}</div>}
                <div className="mt-1 truncate font-mono text-[10px]">
                  commit {commitSha.slice(0, shortCommitShaLength)}
                </div>
                <div className="mt-1 truncate font-mono text-[10px]">
                  run {scope.runId}
                </div>
              </div>
            </aside>
          </ResizablePanel>

          <ResizableHandle />

          <ResizablePanel defaultSize="76%" minSize="50%">
            <section className="bg-card flex h-full min-w-0 flex-col">
              {selectedArtifact ? (
                <>
                  <div className="border-border flex h-[66px] shrink-0 items-center justify-between gap-3 border-b px-4">
                    <div className="flex min-w-0 items-center gap-2.5">
                      <span className="bg-accent flex size-8 shrink-0 items-center justify-center rounded-md">
                        <ArtifactKindIcon kind={selectedArtifact.kind} />
                      </span>
                      <span className="min-w-0">
                        <span className="block truncate font-mono text-xs font-semibold">
                          {getArtifactFileName(selectedArtifact)}
                        </span>
                        <span className="text-muted-foreground block truncate text-[11px]">
                          {selectedArtifact.path}
                        </span>
                      </span>
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        disabled={loadedContent === null}
                        onClick={() => void handleCopy()}
                      >
                        <Copy />
                        <span className="hidden md:inline">
                          Copy {artifactKindLabels[selectedArtifact.kind]}
                        </span>
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        disabled={loadedContent === null}
                        onClick={() => {
                          if (loadedContent !== null) {
                            downloadTextFile(
                              getArtifactFileName(selectedArtifact),
                              loadedContent,
                              artifactMimeTypes[selectedArtifact.kind],
                            );
                          }
                        }}
                      >
                        <Download />
                        <span className="hidden sm:inline">Download</span>
                      </Button>
                    </div>
                  </div>

                  <div className="min-h-0 flex-1 overflow-hidden">
                    <ArtifactContent entry={selectedArtifact} file={file} />
                  </div>
                </>
              ) : (
                <div className="text-muted-foreground flex h-full items-center justify-center text-sm">
                  No generated artifacts are available.
                </div>
              )}
            </section>
          </ResizablePanel>
        </ResizablePanelGroup>
      </DialogContent>
    </Dialog>
  );
}
