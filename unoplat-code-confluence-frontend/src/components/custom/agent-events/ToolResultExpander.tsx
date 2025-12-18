import React from "react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { truncateMessage } from "@/lib/agent-events-utils";
import type { ToolResultExpanderProps } from "@/types/agent-events";

const DEFAULT_MAX_LENGTH = 50;

export function ToolResultExpander({
  message,
  maxLength = DEFAULT_MAX_LENGTH,
}: ToolResultExpanderProps): React.ReactElement {
  const [isOpen, setIsOpen] = React.useState(false);
  const { text: truncatedText, isTruncated } = truncateMessage(
    message,
    maxLength,
  );

  // If message is short enough, just render it directly
  if (!isTruncated) {
    return (
      <span className="text-muted-foreground break-all whitespace-pre-wrap">
        {message}
      </span>
    );
  }

  return (
    <Collapsible
      open={isOpen}
      onOpenChange={setIsOpen}
      className="flex flex-col gap-1"
    >
      <p className="text-muted-foreground inline break-all whitespace-pre-wrap">
        {isOpen ? "" : truncatedText}
        <CollapsibleTrigger asChild>
          <Button variant="link" size="sm" className="h-auto p-0 text-xs">
            [{isOpen ? "less" : "more"}]
          </Button>
        </CollapsibleTrigger>
      </p>
      <CollapsibleContent>
        <pre className="border-border bg-muted/50 max-h-[200px] overflow-auto rounded-md border p-2 text-xs break-all whitespace-pre-wrap">
          {message}
        </pre>
      </CollapsibleContent>
    </Collapsible>
  );
}
