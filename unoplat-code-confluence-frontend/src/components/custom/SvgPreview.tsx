import * as React from "react";
import { Fullscreen, LocateFixed, Minus, Plus } from "lucide-react";
import { TransformComponent, TransformWrapper } from "react-zoom-pan-pinch";

import { Button } from "@/components/ui/button";
import { ButtonGroup, ButtonGroupText } from "@/components/ui/button-group";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface SvgPreviewProps {
  source: string;
  fileName: string;
}

function SvgControl({
  label,
  children,
  onClick,
}: {
  label: string;
  children: React.ReactNode;
  onClick: () => void;
}): React.ReactElement {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="size-8 rounded-none"
          aria-label={label}
          onClick={onClick}
        >
          {children}
        </Button>
      </TooltipTrigger>
      <TooltipContent side="top">{label}</TooltipContent>
    </Tooltip>
  );
}

export function SvgPreview({
  source,
  fileName,
}: SvgPreviewProps): React.ReactElement {
  const viewerRef = React.useRef<HTMLDivElement>(null);
  const [objectUrl, setObjectUrl] = React.useState<string | null>(null);
  const [zoomPercent, setZoomPercent] = React.useState(100);

  React.useEffect(() => {
    const blob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
    const nextObjectUrl = URL.createObjectURL(blob);
    setObjectUrl(nextObjectUrl);

    return () => URL.revokeObjectURL(nextObjectUrl);
  }, [source]);

  const handleFullscreen = async (): Promise<void> => {
    if (!viewerRef.current) return;

    if (document.fullscreenElement === viewerRef.current) {
      await document.exitFullscreen();
      return;
    }

    await viewerRef.current.requestFullscreen();
  };

  return (
    <TooltipProvider delayDuration={250}>
      <TransformWrapper
        key={`${fileName}-${source.length}`}
        initialScale={1}
        minScale={0.25}
        maxScale={4}
        centerOnInit
        centerZoomedOut
        limitToBounds={false}
        wheel={{ step: 0.12 }}
        doubleClick={{ mode: "toggle", step: 0.7 }}
        onTransform={(_, state) => {
          setZoomPercent(Math.round(state.scale * 100));
        }}
      >
        {({ zoomIn, zoomOut, centerView }) => (
          <div
            ref={viewerRef}
            className="bg-muted fullscreen:p-6 relative flex h-full min-h-0 w-full items-center justify-center overflow-hidden p-4"
          >
            <div className="border-border bg-card h-full w-full overflow-hidden rounded-lg border shadow-md">
              <TransformComponent
                wrapperStyle={{ width: "100%", height: "100%" }}
                contentStyle={{
                  width: "100%",
                  height: "100%",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {objectUrl ? (
                  <img
                    src={objectUrl}
                    alt={`Preview of ${fileName}`}
                    draggable={false}
                    className="max-h-full max-w-full select-none"
                  />
                ) : (
                  <div className="text-muted-foreground text-sm">
                    Preparing preview…
                  </div>
                )}
              </TransformComponent>
            </div>

            <ButtonGroup className="bg-card absolute right-7 bottom-7 overflow-hidden rounded-md border shadow-md">
              <SvgControl label="Zoom out" onClick={() => zoomOut(0.2)}>
                <Minus />
              </SvgControl>
              <ButtonGroupText className="min-w-14 justify-center rounded-none border-y-0 px-2 font-mono text-xs tabular-nums shadow-none">
                {zoomPercent}%
              </ButtonGroupText>
              <SvgControl label="Zoom in" onClick={() => zoomIn(0.2)}>
                <Plus />
              </SvgControl>
              <SvgControl label="Fit to view" onClick={() => centerView(1)}>
                <LocateFixed />
              </SvgControl>
              <SvgControl
                label="Toggle fullscreen"
                onClick={() => void handleFullscreen()}
              >
                <Fullscreen />
              </SvgControl>
            </ButtonGroup>
          </div>
        )}
      </TransformWrapper>
    </TooltipProvider>
  );
}
