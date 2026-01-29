import { createFileRoute } from "@tanstack/react-router";
import ToolConfigPage from "@/pages/ToolConfigPage";

export const Route = createFileRoute("/settings/tool-config")({
  beforeLoad: () => ({ getTitle: () => "Tool Configuration" }),
  component: ToolConfigPage,
});
