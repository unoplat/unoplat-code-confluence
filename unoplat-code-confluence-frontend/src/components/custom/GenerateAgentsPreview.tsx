import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Copy } from "lucide-react";
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
import type { AgentMdCodebaseOutput } from "@/features/repository-agent-snapshots/schema";
import { agentMdOutputToMarkdown } from "@/lib/agent-md-to-markdown";

interface GenerateAgentsPreviewProps {
  codebases: Record<string, AgentMdCodebaseOutput>;
  repositoryName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDownloadAll: () => void;
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
  };

  const codebaseEntries = Object.entries(codebases);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="h-[80vh] max-w-5xl">
        <DialogHeader className="text-center">
          <DialogTitle className="text-center">
            Preview {repositoryName}
          </DialogTitle>
          <DialogDescription className="text-center">
            Preview and download the generated agents documentation.
          </DialogDescription>
        </DialogHeader>
        <div className="-mt-2 flex items-center justify-center gap-2">
          <Button size="sm" onClick={onDownloadAll}>
            Download All
          </Button>
        </div>
        <ScrollArea className="border-border bg-background h-[60vh] rounded-md border">
          <Accordion type="multiple" defaultValue={[]} className="w-full px-4">
            {codebaseEntries.map(([codebaseName, agentMdOutput]) => {
              const codebaseMarkdown = agentMdOutputToMarkdown(agentMdOutput, {
                title: codebaseName,
              });

              return (
                <AccordionItem
                  key={codebaseName}
                  value={codebaseName}
                  className="border-b"
                >
                  <div className="flex items-center gap-2">
                    <AccordionTrigger className="flex-1 py-4 hover:no-underline">
                      <span className="text-left font-medium">
                        {codebaseName}
                      </span>
                    </AccordionTrigger>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        void handleCopyCodebase(codebaseMarkdown);
                      }}
                      aria-label={`Copy markdown for ${codebaseName}`}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>

                  <AccordionContent className="pb-4">
                    <div className="border-border bg-muted/50 dark:bg-muted rounded-md border p-4">
                      <MDXEditor
                        markdown={codebaseMarkdown}
                        readOnly
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
                            codeBlockLanguages: {
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
                            },
                          }),
                          markdownShortcutPlugin(),
                        ]}
                        contentEditableClassName="prose prose-sm max-w-none dark:prose-invert mdx-editor-content"
                        className="mdx-editor-wrapper mdx-editor-theme h-full"
                      />
                    </div>
                  </AccordionContent>
                </AccordionItem>
              );
            })}
          </Accordion>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
