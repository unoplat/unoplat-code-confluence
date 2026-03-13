import React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Label } from "@/components/ui/label";
import { Copy, Download, FolderKanban } from "lucide-react";
import { toast } from "sonner";
import "@mdxeditor/editor/style.css";
import {
  MDXEditor,
  headingsPlugin,
  listsPlugin,
  linkPlugin,
  quotePlugin,
  thematicBreakPlugin,
  tablePlugin,
  codeBlockPlugin,
  codeMirrorPlugin,
  markdownShortcutPlugin,
} from "@mdxeditor/editor";
import type {
  AgentMdCodebaseOutput,
  AgentMdProgrammingLanguageMetadata,
} from "@/features/repository-agent-snapshots/schema";
import {
  agentMdOutputToMarkdown,
  codebasesToMarkdown,
} from "@/lib/agent-md-to-markdown";

function buildTechStackSubtitle(
  metadata: AgentMdProgrammingLanguageMetadata | null | undefined,
): string | null {
  if (!metadata) return null;
  const parts: string[] = [];
  if (metadata.primary_language) parts.push(metadata.primary_language);
  if (metadata.package_manager) parts.push(metadata.package_manager);
  return parts.length > 0 ? parts.join(" \u00b7 ") : null;
}

interface GenerateAgentsPreviewProps {
  codebases: Record<string, AgentMdCodebaseOutput>;
  repositoryName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDownloadAll: () => void;
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

function buildMarkdownEditorKey(codebaseName: string, markdown: string): string {
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
        codeBlockPlugin({
          defaultCodeBlockLanguage: "txt",
        }),
        codeMirrorPlugin({
          codeBlockLanguages,
        }),
        markdownShortcutPlugin(),
      ]}
      contentEditableClassName="prose prose-sm max-w-none dark:prose-invert mdx-editor-content"
      className="mdx-editor-wrapper mdx-editor-theme h-full"
    />
  );
}

export function GenerateAgentsPreview({
  codebases,
  repositoryName,
  open,
  onOpenChange,
  onDownloadAll,
}: GenerateAgentsPreviewProps): React.ReactElement {
  const handleCopyCodebase = async (content: string): Promise<void> => {
    await navigator.clipboard.writeText(content);
    toast.success("Copied to clipboard");
  };

  const handleCopyAll = async (): Promise<void> => {
    const allMarkdown = codebasesToMarkdown(codebases, {
      title: repositoryName,
    });
    await navigator.clipboard.writeText(allMarkdown);
    toast.success("Copied all codebases to clipboard");
  };

  const codebaseEntries = Object.entries(codebases);
  const codebaseCount = codebaseEntries.length;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent size="md" className="flex max-h-[80vh] flex-col">
        <DialogHeader>
          <DialogTitle>{repositoryName}</DialogTitle>
          <DialogDescription>
            Preview and download the generated agents documentation.
          </DialogDescription>
        </DialogHeader>
        <Separator />
        <div className="flex justify-center">
          <Badge variant="section">Codebases</Badge>
        </div>
        <ScrollArea className="border-border bg-background min-h-0 rounded-md border [&>[data-radix-scroll-area-viewport]]:max-h-[50vh]">
          <Accordion type="multiple" defaultValue={[]} className="w-full">
            {codebaseEntries.map(([codebaseName, agentMdOutput]) => {
              const codebaseMarkdown = agentMdOutputToMarkdown(agentMdOutput, {
                title: codebaseName,
              });
              const editorKey = buildMarkdownEditorKey(
                codebaseName,
                codebaseMarkdown,
              );
              const techStack = buildTechStackSubtitle(
                agentMdOutput.programming_language_metadata,
              );

              return (
                <AccordionItem
                  key={codebaseName}
                  value={codebaseName}
                  className="group border-b last:border-b-0 data-[state=open]:border-primary/20"
                >
                  <div className="flex items-center gap-3 px-3">
                    <div className="bg-primary/10 flex h-8 w-8 shrink-0 items-center justify-center rounded-md">
                      <FolderKanban className="text-primary h-4 w-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <AccordionTrigger className="py-3 hover:no-underline">
                        <div className="flex flex-col items-start gap-0.5">
                          <Label
                            size="sm"
                            weight="medium"
                            className="text-left"
                          >
                            {codebaseName}
                          </Label>
                          {techStack && (
                            <Label
                              size="xs"
                              state="muted"
                              weight="normal"
                              className="text-left"
                            >
                              {techStack}
                            </Label>
                          )}
                        </div>
                      </AccordionTrigger>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-7 w-7 shrink-0 p-0"
                      onClick={(e) => {
                        e.stopPropagation();
                        void handleCopyCodebase(codebaseMarkdown);
                      }}
                      aria-label={`Copy markdown for ${codebaseName}`}
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </Button>
                  </div>

                  <AccordionContent className="px-3 pb-3">
                    <div className="border-border bg-muted/50 dark:bg-muted rounded-md border p-4">
                      <ReadonlyMarkdownPreview
                        markdown={codebaseMarkdown}
                        editorKey={editorKey}
                      />
                    </div>
                  </AccordionContent>
                </AccordionItem>
              );
            })}
          </Accordion>
        </ScrollArea>
        <Separator />
        <DialogFooter className="flex-row items-center justify-between gap-2 sm:justify-between">
          <Label size="sm" state="muted" weight="normal">
            {codebaseCount} {codebaseCount === 1 ? "codebase" : "codebases"}{" "}
            generated
          </Label>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => void handleCopyAll()}
            >
              <Copy className="h-4 w-4" />
              Copy All
            </Button>
            <Button size="sm" onClick={onDownloadAll}>
              <Download className="h-4 w-4" />
              Download All
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
