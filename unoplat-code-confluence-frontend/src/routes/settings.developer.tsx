import { createFileRoute } from "@tanstack/react-router";
import DeveloperModePage from "../pages/DeveloperModePage";

export const Route = createFileRoute("/settings/developer")({
  beforeLoad: () => ({ getTitle: () => "Developer Mode" }),
  component: DeveloperModePage,
});
