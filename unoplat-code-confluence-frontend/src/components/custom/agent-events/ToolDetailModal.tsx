import React from "react";
import { Copy, Wrench } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { RepositoryAgentEvent } from "@/features/repository-agent-snapshots/schema";
import type { ToolDetailModalProps } from "@/types/agent-events";

function getToolName(callEvent?: RepositoryAgentEvent): string {
  if (
    typeof callEvent?.tool_name === "string" &&
    callEvent.tool_name.trim().length > 0
  ) {
    return callEvent.tool_name;
  }

  if (
    typeof callEvent?.message === "string" &&
    callEvent.message.trim().length > 0
  ) {
    return callEvent.message.replace(/^Calling\s+/, "");
  }

  return callEvent?.event ?? "Tool Call";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function formatToolArgs(callEvent?: RepositoryAgentEvent): string {
  if (isRecord(callEvent?.tool_args)) {
    return JSON.stringify(callEvent.tool_args, null, 2);
  }

  if (
    typeof callEvent?.message === "string" &&
    callEvent.message.trim().length > 0
  ) {
    return callEvent.message;
  }

  return "-";
}

function stripToolResultPrefix(value: string): string {
  return value.replace(/^Tool result:\s*/, "");
}

function getResultContent(resultEvent?: RepositoryAgentEvent): string {
  if (
    typeof resultEvent?.tool_result_content === "string" &&
    resultEvent.tool_result_content.length > 0
  ) {
    return resultEvent.tool_result_content;
  }

  if (
    typeof resultEvent?.message === "string" &&
    resultEvent.message.length > 0
  ) {
    return stripToolResultPrefix(resultEvent.message);
  }

  return "-";
}

function getSourceHint(callEvent?: RepositoryAgentEvent): string | null {
  if (!isRecord(callEvent?.tool_args)) {
    return null;
  }

  const filePath = callEvent.tool_args.file_path;
  if (typeof filePath === "string" && filePath.length > 0) {
    return filePath;
  }

  const path = callEvent.tool_args.path;
  if (typeof path === "string" && path.length > 0) {
    return path;
  }

  const filePathAlt = callEvent.tool_args.filepath;
  if (typeof filePathAlt === "string" && filePathAlt.length > 0) {
    return filePathAlt;
  }

  return null;
}

async function copyToClipboard(value: string): Promise<void> {
  if (typeof navigator === "undefined" || !navigator.clipboard) {
    return;
  }

  if (value.length === 0) {
    return;
  }

  try {
    await navigator.clipboard.writeText(value);
  } catch {
    // Ignore clipboard errors; the dialog remains fully usable.
  }
}

export function ToolDetailModal({
  open,
  onOpenChange,
  item,
}: ToolDetailModalProps): React.ReactElement {
  const formattedArgs = formatToolArgs(item?.callEvent);
  const fullResult = getResultContent(item?.resultEvent);
  const sourceHint = getSourceHint(item?.callEvent);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[560px] gap-0 p-0">
        <DialogHeader className="border-border border-b px-5 py-4">
          <div className="flex items-center gap-3 pr-8">
            <Badge
              variant="secondary"
              className="h-5 rounded-sm border-0 px-2 text-[10px] tracking-wide uppercase"
            >
              <Wrench className="h-3 w-3" />
              Tool Call
            </Badge>
            <DialogTitle className="min-w-0 truncate text-lg font-medium">
              {getToolName(item?.callEvent)}
            </DialogTitle>
          </div>
        </DialogHeader>

        <div className="space-y-5 px-5 py-4">
          <section className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground text-xs tracking-wide uppercase">
                Arguments
              </span>
              <div className="bg-border h-px flex-1" />
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-5 gap-1 px-2 text-[11px]"
                onClick={() => {
                  void copyToClipboard(formattedArgs);
                }}
              >
                <Copy className="h-3 w-3" />
                Copy
              </Button>
            </div>

            <ScrollArea className="bg-muted/40 h-[106px] rounded-md border p-3">
              <pre className="font-mono text-xs whitespace-pre-wrap">
                {formattedArgs}
              </pre>
            </ScrollArea>
          </section>

          <section className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5">
                <span className="bg-success h-1.5 w-1.5 rounded-full" />
                <span className="text-muted-foreground text-xs tracking-wide uppercase">
                  Result
                </span>
              </div>
              <div className="bg-border h-px flex-1" />
              {sourceHint ? (
                <span className="text-muted-foreground max-w-[140px] truncate text-[11px]">
                  {sourceHint}
                </span>
              ) : null}
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-5 gap-1 px-2 text-[11px]"
                onClick={() => {
                  void copyToClipboard(fullResult);
                }}
              >
                <Copy className="h-3 w-3" />
                Copy
              </Button>
            </div>

            <ScrollArea className="h-[200px] rounded-md bg-zinc-950 p-3">
              <pre className="font-mono text-xs whitespace-pre-wrap text-zinc-100">
                {fullResult}
              </pre>
            </ScrollArea>
          </section>
        </div>
      </DialogContent>
    </Dialog>
  );
}
