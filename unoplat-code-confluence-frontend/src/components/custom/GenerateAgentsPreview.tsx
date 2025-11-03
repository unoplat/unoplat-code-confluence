import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import '@mdxeditor/editor/style.css';
import { MDXEditor, headingsPlugin, listsPlugin, linkPlugin, quotePlugin, thematicBreakPlugin, tablePlugin, codeBlockPlugin, codeMirrorPlugin } from '@mdxeditor/editor';

interface GenerateAgentsPreviewProps {
  content: string;
  fileName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function GenerateAgentsPreview({ content, fileName, open, onOpenChange }: GenerateAgentsPreviewProps): React.ReactElement {
  const handleDownload = (): void => {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleCopy = async (): Promise<void> => {
    await navigator.clipboard.writeText(content);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl h-[80vh]">
        <DialogHeader className="text-center">
          <DialogTitle className="text-center">Preview {fileName}</DialogTitle>
          <DialogDescription className="text-center">
            Preview and download the generated agents documentation.
          </DialogDescription>
        </DialogHeader>
        <div className="flex items-center justify-center gap-2 -mt-2">
          <Button size="sm" onClick={handleDownload}>Download</Button>
          <Button size="sm" variant="outline" onClick={handleCopy}>Copy</Button>
        </div>
        <div className="grid grid-cols-1 gap-4">
          <ScrollArea className="h-[60vh] border rounded-md p-4 bg-background">
            <MDXEditor
              markdown={content}
              readOnly={true}
              plugins={[
                headingsPlugin(),
                listsPlugin(),
                linkPlugin(),
                quotePlugin(),
                thematicBreakPlugin(),
                tablePlugin(),
                codeBlockPlugin({
                  defaultCodeBlockLanguage: 'txt'
                }),
                codeMirrorPlugin({
                  codeBlockLanguages: {
                    js: 'JavaScript',
                    jsx: 'JSX',
                    ts: 'TypeScript',
                    tsx: 'TSX',
                    py: 'Python',
                    css: 'CSS',
                    json: 'JSON',
                    md: 'Markdown',
                    txt: 'Plain Text',
                    bash: 'Bash',
                    shell: 'Shell',
                    yaml: 'YAML',
                    yml: 'YAML',
                    toml: 'TOML'
                  }
                })
              ]}
              contentEditableClassName="prose prose-sm max-w-none dark:prose-invert mdx-editor-content"
              className="h-full mdx-editor-wrapper"
            />
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  );
}


