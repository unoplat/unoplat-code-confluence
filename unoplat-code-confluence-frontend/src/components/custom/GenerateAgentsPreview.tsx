import * as React from "react";
import {
  ChevronRight,
  Copy,
  Download,
  FileText,
  Folder,
  Network,
  Search,
  X,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { toast } from "sonner";
import "@mdxeditor/editor/style.css";
import {
  MDXEditor,
  codeBlockPlugin,
  codeMirrorPlugin,
  headingsPlugin,
  linkPlugin,
  listsPlugin,
  markdownShortcutPlugin,
  quotePlugin,
  tablePlugin,
  thematicBreakPlugin,
} from "@mdxeditor/editor";

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
import type {
  AgentMdCodebaseOutput,
  AgentMdProgrammingLanguageMetadata,
} from "@/features/repository-agent-snapshots/schema";
import { agentMdOutputToMarkdown } from "@/lib/agent-md-to-markdown";
import { cn } from "@/lib/utils";

export interface GeneratedArtifact {
  codebaseName: string;
  fileName: string;
  type: "markdown" | "svg";
  content: string;
  description?: string;
  sizeLabel?: string;
  width?: number;
  height?: number;
}

interface GenerateAgentsPreviewProps {
  codebases: Record<string, AgentMdCodebaseOutput>;
  repositoryName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDownloadAll: () => void;
  artifacts?: GeneratedArtifact[];
  generatedAt?: string;
  runId?: string;
}

interface ArtifactGroup {
  codebaseName: string;
  metadata?: AgentMdProgrammingLanguageMetadata | null;
  artifacts: ViewerArtifact[];
}

interface ViewerArtifact extends GeneratedArtifact {
  id: string;
}

const codeBlockLanguages: Record<string, string> = {
  js: "JavaScript",
  jsx: "JSX",
  ts: "TypeScript",
  tsx: "TSX",
  py: "Python",
  css: "CSS",
  json: "JSON",
  md: "Markdown",
  txt: "Plain Text",
  bash: "Bash",
  shell: "Shell",
  yaml: "YAML",
  yml: "YAML",
  toml: "TOML",
};

function buildMarkdownEditorKey(
  codebaseName: string,
  markdown: string,
): string {
  let hash = 0;
  for (let index = 0; index < markdown.length; index += 1) {
    hash = (hash * 31 + markdown.charCodeAt(index)) >>> 0;
  }
  return `${codebaseName}-${hash}-${markdown.length}`;
}

function ReadonlyMarkdownPreview({
  markdown,
  editorKey,
}: {
  markdown: string;
  editorKey: string;
}): React.ReactElement {
  return (
    <MDXEditor
      key={editorKey}
      markdown={markdown}
      readOnly
      suppressHtmlProcessing
      plugins={[
        headingsPlugin(),
        listsPlugin(),
        linkPlugin(),
        quotePlugin(),
        thematicBreakPlugin(),
        tablePlugin(),
        codeBlockPlugin({ defaultCodeBlockLanguage: "txt" }),
        codeMirrorPlugin({ codeBlockLanguages }),
        markdownShortcutPlugin(),
      ]}
      contentEditableClassName="prose prose-sm max-w-none dark:prose-invert mdx-editor-content"
      className="mdx-editor-wrapper mdx-editor-theme min-h-full"
    />
  );
}

function formatBytes(content: string): string {
  const bytes = new Blob([content]).size;
  if (bytes < 1024) return `${bytes} B`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

function buildTechStackSubtitle(
  metadata: AgentMdProgrammingLanguageMetadata | null | undefined,
): string | null {
  if (!metadata) return null;
  return [metadata.primary_language, metadata.package_manager]
    .filter(Boolean)
    .join(" · ");
}

function downloadArtifact(artifact: ViewerArtifact): void {
  const mimeType =
    artifact.type === "svg"
      ? "image/svg+xml;charset=utf-8"
      : "text/markdown;charset=utf-8";
  const url = URL.createObjectURL(
    new Blob([artifact.content], { type: mimeType }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = artifact.fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function GenerateAgentsPreview({
  codebases,
  repositoryName,
  open,
  onOpenChange,
  onDownloadAll,
  artifacts = [],
  generatedAt,
  runId,
}: GenerateAgentsPreviewProps): React.ReactElement {
  const viewerArtifacts = React.useMemo<ViewerArtifact[]>(() => {
    const markdownArtifacts = Object.entries(codebases).map(
      ([codebaseName, output]): ViewerArtifact => ({
        id: `${codebaseName}:AGENTS.md`,
        codebaseName,
        fileName: "AGENTS.md",
        type: "markdown",
        content: agentMdOutputToMarkdown(output, { title: codebaseName }),
        description: "Generated agents documentation",
      }),
    );

    const additionalArtifacts = artifacts.map((artifact, index) => ({
      ...artifact,
      id: `${artifact.codebaseName}:${artifact.fileName}:${index}`,
    }));

    return [...markdownArtifacts, ...additionalArtifacts];
  }, [artifacts, codebases]);

  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedArtifactId, setSelectedArtifactId] = React.useState("");
  const [openCodebases, setOpenCodebases] = React.useState<Set<string>>(
    () => new Set(),
  );

  React.useEffect(() => {
    if (!open || viewerArtifacts.length === 0) return;

    const selectedStillExists = viewerArtifacts.some(
      (artifact) => artifact.id === selectedArtifactId,
    );
    if (!selectedStillExists) {
      const firstSvg = viewerArtifacts.find(
        (artifact) => artifact.type === "svg",
      );
      const nextArtifact = firstSvg ?? viewerArtifacts[0];
      setSelectedArtifactId(nextArtifact.id);
      setOpenCodebases((current) => {
        const next = new Set(current);
        next.add(nextArtifact.codebaseName);
        return next;
      });
    }
  }, [open, selectedArtifactId, viewerArtifacts]);

  const selectedArtifact =
    viewerArtifacts.find((artifact) => artifact.id === selectedArtifactId) ??
    viewerArtifacts[0];

  const groups = React.useMemo<ArtifactGroup[]>(() => {
    const query = searchQuery.trim().toLocaleLowerCase();
    const codebaseNames = new Set([
      ...Object.keys(codebases),
      ...viewerArtifacts.map((artifact) => artifact.codebaseName),
    ]);

    return [...codebaseNames]
      .map((codebaseName) => {
        const codebaseMatches = codebaseName
          .toLocaleLowerCase()
          .includes(query);
        const matchingArtifacts = viewerArtifacts.filter(
          (artifact) =>
            artifact.codebaseName === codebaseName &&
            (codebaseMatches ||
              artifact.fileName.toLocaleLowerCase().includes(query)),
        );

        return {
          codebaseName,
          metadata: codebases[codebaseName]?.programming_language_metadata,
          artifacts: matchingArtifacts,
        };
      })
      .filter((group) => group.artifacts.length > 0);
  }, [codebases, searchQuery, viewerArtifacts]);

  const handleCopy = async (): Promise<void> => {
    if (!selectedArtifact) return;
    await navigator.clipboard.writeText(selectedArtifact.content);
    toast.success(`${selectedArtifact.fileName} copied to clipboard`);
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
              {viewerArtifacts.length}{" "}
              {viewerArtifacts.length === 1 ? "artifact" : "artifacts"} across{" "}
              {Object.keys(codebases).length}{" "}
              {Object.keys(codebases).length === 1 ? "codebase" : "codebases"}
              <span className="sr-only"> for {repositoryName}</span>
            </DialogDescription>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onDownloadAll}
            >
              <Download />
              <span className="hidden sm:inline">Download all</span>
            </Button>
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
                Codebases · {groups.length}
              </div>

              <ScrollArea className="min-h-0 flex-1" viewportClassName="pr-1">
                {groups.length > 0 ? (
                  <div className="space-y-0.5">
                    {groups.map((group) => {
                      const isOpen = openCodebases.has(group.codebaseName);
                      const techStack = buildTechStackSubtitle(group.metadata);
                      return (
                        <Collapsible key={group.codebaseName} open={isOpen}>
                          <button
                            type="button"
                            onClick={() => {
                              setOpenCodebases((current) => {
                                const next = new Set(current);
                                if (next.has(group.codebaseName))
                                  next.delete(group.codebaseName);
                                else next.add(group.codebaseName);
                                return next;
                              });
                            }}
                            className="hover:bg-accent focus-visible:ring-ring flex h-12 w-full items-center gap-2 rounded-md px-2 text-left outline-none focus-visible:ring-2"
                            aria-expanded={isOpen}
                          >
                            <Folder className="size-4 shrink-0" />
                            <span className="min-w-0 flex-1">
                              <span className="block truncate text-xs font-semibold">
                                {group.codebaseName}
                              </span>
                              <span className="text-muted-foreground block truncate text-[11px]">
                                {[
                                  techStack,
                                  `${group.artifacts.length} ${group.artifacts.length === 1 ? "artifact" : "artifacts"}`,
                                ]
                                  .filter(Boolean)
                                  .join(" · ")}
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
                                  artifact.id === selectedArtifact?.id;
                                return (
                                  <button
                                    key={artifact.id}
                                    type="button"
                                    onClick={() =>
                                      setSelectedArtifactId(artifact.id)
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
                                      {artifact.type === "svg" ? (
                                        <Network className="size-3.5" />
                                      ) : (
                                        <FileText className="size-3.5" />
                                      )}
                                    </span>
                                    <span className="min-w-0 flex-1">
                                      <span className="block truncate font-mono text-[11px] font-medium">
                                        {artifact.fileName}
                                      </span>
                                      <span className="text-muted-foreground block truncate text-[10px]">
                                        {artifact.type === "svg"
                                          ? `SVG${artifact.width && artifact.height ? ` · ${artifact.width} × ${artifact.height}` : ""}`
                                          : `Markdown · ${artifact.sizeLabel ?? formatBytes(artifact.content)}`}
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

              {(generatedLabel || runId) && (
                <div className="border-border text-muted-foreground mt-3 shrink-0 border-t px-2 pt-3 text-[11px]">
                  {generatedLabel && <div>{generatedLabel}</div>}
                  {runId && (
                    <div className="mt-1 truncate font-mono text-[10px]">
                      run {runId}
                    </div>
                  )}
                </div>
              )}
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
                        {selectedArtifact.type === "svg" ? (
                          <Network />
                        ) : (
                          <FileText />
                        )}
                      </span>
                      <span className="min-w-0">
                        <span className="block truncate font-mono text-xs font-semibold">
                          {selectedArtifact.fileName}
                        </span>
                        <span className="text-muted-foreground block truncate text-[11px]">
                          {selectedArtifact.description ??
                            (selectedArtifact.type === "svg"
                              ? "SVG artifact"
                              : "Generated Markdown")}
                        </span>
                      </span>
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => void handleCopy()}
                      >
                        <Copy />
                        <span className="hidden md:inline">
                          Copy{" "}
                          {selectedArtifact.type === "svg" ? "SVG" : "Markdown"}
                        </span>
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        onClick={() => downloadArtifact(selectedArtifact)}
                      >
                        <Download />
                        <span className="hidden sm:inline">Download</span>
                      </Button>
                    </div>
                  </div>

                  <div className="min-h-0 flex-1 overflow-hidden">
                    {selectedArtifact.type === "svg" ? (
                      <SvgPreview
                        source={selectedArtifact.content}
                        fileName={selectedArtifact.fileName}
                      />
                    ) : (
                      <ScrollArea
                        className="bg-muted h-full p-4"
                        viewportClassName="pr-3"
                      >
                        <div className="border-border bg-card mx-auto min-h-full max-w-3xl rounded-lg border p-5 shadow-sm">
                          <ReadonlyMarkdownPreview
                            markdown={selectedArtifact.content}
                            editorKey={buildMarkdownEditorKey(
                              selectedArtifact.id,
                              selectedArtifact.content,
                            )}
                          />
                        </div>
                      </ScrollArea>
                    )}
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
