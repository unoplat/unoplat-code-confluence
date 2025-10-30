import { createFileRoute } from "@tanstack/react-router";
import { SubmittedJobsDataTable } from "@/components/custom/SubmittedJobsDataTable";
import React from "react";

export const Route = createFileRoute("/_app/repositoryManagement")({
  component: RepositoryManagementPage,
  beforeLoad: () => {
    return {
      getTitle: () => "Ingestion Management",
    };
  },
});

function RepositoryManagementPage(): React.ReactElement {
  return (
    <div className="flex flex-col gap-4">
      <SubmittedJobsDataTable />
    </div>
  );
}
