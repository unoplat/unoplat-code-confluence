import architectureSvg from "@/assets/images/architecture.svg";
import { ImageZoom } from "fumadocs-ui/components/image-zoom";

export function ArchitectureDiagramShowcase() {
  return (
    <figure className="my-6 overflow-hidden rounded-xl border border-fd-border bg-fd-card">
      <div className="overflow-x-auto bg-white p-3">
        <ImageZoom
          src={architectureSvg}
          alt="Unoplat Code Confluence system architecture, generated as architecture.svg"
          width={3469}
          height={942}
          className="mx-auto h-auto w-full max-w-none rounded-md"
        />
      </div>
      <figcaption className="border-t border-fd-border px-4 py-3 text-sm text-fd-muted-foreground">
        Repository-root <code>architecture.svg</code> generated for this project.
        Click the diagram to zoom.
      </figcaption>
    </figure>
  );
}
