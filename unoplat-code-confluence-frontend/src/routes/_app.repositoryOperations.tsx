import React from "react";
import { createFileRoute } from "@tanstack/react-router";
import { IngestedRepositoriesDataTable } from "@/components/custom/IngestedRepositoriesDataTable";

export const Route = createFileRoute("/_app/repositoryOperations")({
  component: RepositoryOperationsPage,
  beforeLoad: () => {
    return {
      getTitle: () => "Repository Operations",
    };
  },
});

function RepositoryOperationsPage(): React.ReactElement {
  return (
    <div className="flex flex-col gap-4">
      <IngestedRepositoriesDataTable />
    </div>
  );
}
