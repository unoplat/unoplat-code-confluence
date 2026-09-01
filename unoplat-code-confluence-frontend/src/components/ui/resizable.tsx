import * as React from "react";
import { GripVertical } from "lucide-react";
import * as ResizablePrimitive from "react-resizable-panels";

import { cn } from "@/lib/utils";

type ResizablePanelGroupProps = Omit<
  React.ComponentProps<typeof ResizablePrimitive.Group>,
  "orientation"
> & {
  direction?: "horizontal" | "vertical";
};

function ResizablePanelGroup({
  className,
  direction = "horizontal",
  ...props
}: ResizablePanelGroupProps): React.ReactElement {
  return (
    <ResizablePrimitive.Group
      data-slot="resizable-panel-group"
      orientation={direction}
      className={cn(
        "flex h-full w-full data-[group]:flex-row",
        direction === "vertical" && "flex-col",
        className,
      )}
      {...props}
    />
  );
}

const ResizablePanel = ResizablePrimitive.Panel;

function ResizableHandle({
  withHandle,
  className,
  ...props
}: React.ComponentProps<typeof ResizablePrimitive.Separator> & {
  withHandle?: boolean;
}): React.ReactElement {
  return (
    <ResizablePrimitive.Separator
      data-slot="resizable-handle"
      className={cn(
        "bg-border focus-visible:ring-ring relative flex w-px items-center justify-center focus-visible:ring-1 focus-visible:ring-offset-1 focus-visible:outline-none aria-[orientation=vertical]:h-px aria-[orientation=vertical]:w-full aria-[orientation=vertical]:after:inset-x-0 aria-[orientation=vertical]:after:inset-y-auto aria-[orientation=vertical]:after:top-1/2 aria-[orientation=vertical]:after:h-1 aria-[orientation=vertical]:after:w-full aria-[orientation=vertical]:after:translate-x-0 aria-[orientation=vertical]:after:-translate-y-1/2 data-[separator]:after:absolute data-[separator]:after:inset-y-0 data-[separator]:after:left-1/2 data-[separator]:after:w-1 data-[separator]:after:-translate-x-1/2",
        className,
      )}
      {...props}
    >
      {withHandle && (
        <div className="bg-border z-10 flex h-4 w-3 items-center justify-center rounded-sm border">
          <GripVertical className="h-2.5 w-2.5" />
        </div>
      )}
    </ResizablePrimitive.Separator>
  );
}

export { ResizablePanelGroup, ResizablePanel, ResizableHandle };
