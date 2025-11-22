import React from "react";
import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/_app")({
  component: AppComponent,
});

function AppComponent(): React.ReactElement {
  return <Outlet />;
}
