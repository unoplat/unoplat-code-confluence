import React from "react";
import type { ColumnDef } from "@tanstack/react-table";
import type {
  ParentWorkflowJobResponse,
  JobStatus,
  RepositoryWorkflowOperation,
} from "@/types";
import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import {
  Ellipsis,
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  Clock,
  PauseCircle,
  RefreshCw,
  Cpu,
  FileCode,
} from "lucide-react";

export const getStatusIcon = (status: JobStatus): React.ReactNode => {
  switch (status) {
    case "COMPLETED":
      return <CheckCircle className="text-success h-4 w-4" />;
    case "FAILED":
      return <AlertCircle className="text-destructive h-4 w-4" />;
    case "TIMED_OUT":
      return <Clock className="text-destructive h-4 w-4" />;
    case "SUBMITTED":
      return <Clock className="text-warning h-4 w-4" />;
    case "RUNNING":
      return <PauseCircle className="text-info h-4 w-4" />;
    case "RETRYING":
      return <RefreshCw className="text-info h-4 w-4" />;
    case "ERROR":
      return <AlertTriangle className="text-destructive h-4 w-4" />;
    default:
      return <Clock className="text-muted-foreground h-4 w-4" />;
  }
};

export const getStatusVariant = (
  status: JobStatus,
): "completed" | "failed" | "pending" | "running" | "cancelled" | "error" => {
  switch (status) {
    case "COMPLETED":
      return "completed";
    case "FAILED":
    case "TIMED_OUT":
      return "failed";
    case "SUBMITTED":
      return "pending";
    case "RUNNING":
    case "RETRYING":
      return "running";
    case "ERROR":
      return "error";
    default:
      return "cancelled";
  }
};

export const getOperationIcon = (
  operation: RepositoryWorkflowOperation,
): React.ReactNode => {
  switch (operation) {
    case "INGESTION":
      return <Cpu className="h-4 w-4" />;
    case "AGENTS_GENERATION":
      return <FileCode className="h-4 w-4" />;
    case "AGENT_MD_UPDATE":
      return <RefreshCw className="h-4 w-4" />;
    default:
      return null;
  }
};

export const getOperationVariant = (
  operation: RepositoryWorkflowOperation,
): "ingestion" | "agents_generation" | "agent_md_update" | "default" => {
  switch (operation) {
    case "INGESTION":
      return "ingestion";
    case "AGENTS_GENERATION":
      return "agents_generation";
    case "AGENT_MD_UPDATE":
      return "agent_md_update";
    default:
      return "default";
  }
};

export const getOperationLabel = (
  operation: RepositoryWorkflowOperation,
): string => {
  switch (operation) {
    case "INGESTION":
      return "Ingestion";
    case "AGENTS_GENERATION":
      return "Agents Generation";
    case "AGENT_MD_UPDATE":
      return "Agent MD Update";
    default:
      return operation;
  }
};

// Static column definitions - defined once outside component scope
export const submittedJobsColumns: ColumnDef<ParentWorkflowJobResponse>[] = [
  {
    accessorKey: "repository_name",
    header: ({ column }): React.ReactNode => (
      <DataTableColumnHeader column={column} label="Repository" />
    ),
    cell: ({ row }): React.ReactNode => {
      const { repository_owner_name, repository_name } = row.original;
      const githubUrl = `https://www.github.com/${repository_owner_name}/${repository_name}`;

      return (
        <div className="flex items-center">
          <a
            href={githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary text-sm font-normal hover:underline"
          >
            {repository_owner_name}/{repository_name}
          </a>
        </div>
      );
    },
    meta: {
      label: "Repository",
      placeholder: "Search repository...",
      variant: "text",
      shortcut: "s",
    },
    enableSorting: false,
    enableColumnFilter: true,
  },
  {
    accessorKey: "operation",
    header: ({ column }): React.ReactNode => (
      <DataTableColumnHeader column={column} label="Operation" />
    ),
    cell: ({ row }): React.ReactNode => (
      <div className="flex items-center gap-2">
        <Badge
          variant={getOperationVariant(row.original.operation)}
          className="gap-1"
        >
          {getOperationIcon(row.original.operation)}
          {getOperationLabel(row.original.operation)}
        </Badge>
      </div>
    ),
    meta: {
      label: "Operation",
      variant: "select",
      options: [
        { label: "Ingestion", value: "INGESTION" },
        { label: "Agents Generation", value: "AGENTS_GENERATION" },
        { label: "Agent MD Update", value: "AGENT_MD_UPDATE" },
      ],
    },
    enableColumnFilter: true,
    enableSorting: false,
  },
  {
    accessorKey: "repository_workflow_run_id",
    header: ({ column }): React.ReactNode => (
      <DataTableColumnHeader column={column} label="Job ID" />
    ),
    cell: ({ row }): React.ReactNode => (
      <div className="flex items-center">
        <span className="text-sm font-normal">
          {row.original.repository_workflow_run_id}
        </span>
      </div>
    ),
    enableSorting: false,
    enableColumnFilter: false,
  },
  {
    accessorKey: "status",
    header: ({ column }): React.ReactNode => (
      <DataTableColumnHeader column={column} label="Status" />
    ),
    cell: ({ row }): React.ReactNode => (
      <div className="flex items-center gap-2">
        <Badge
          variant={getStatusVariant(row.original.status)}
          className="gap-1"
        >
          {getStatusIcon(row.original.status)}
          {row.original.status}
        </Badge>
      </div>
    ),
    meta: {
      label: "Status",
      variant: "select",
      options: [
        { label: "Submitted", value: "SUBMITTED" },
        { label: "Running", value: "RUNNING" },
        { label: "Completed", value: "COMPLETED" },
        { label: "Failed", value: "FAILED" },
        { label: "Timed Out", value: "TIMED_OUT" },
        { label: "Retrying", value: "RETRYING" },
        { label: "Error", value: "ERROR" },
      ],
    },
    enableColumnFilter: true,
  },
  {
    accessorKey: "started_at",
    header: ({ column }): React.ReactNode => (
      <DataTableColumnHeader column={column} label="Started" />
    ),
    cell: ({ row }): React.ReactNode => {
      const date = new Date(row.original.started_at);
      return (
        <div className="flex flex-col">
          <span className="text-sm font-normal">
            {date.toLocaleString(undefined, {
              year: "numeric",
              month: "2-digit",
              day: "2-digit",
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
              hour12: false,
            })}
          </span>
        </div>
      );
    },
    enableSorting: false,
  },
  {
    accessorKey: "completed_at",
    header: ({ column }): React.ReactNode => (
      <DataTableColumnHeader column={column} label="Completed" />
    ),
    cell: ({ row }): React.ReactNode => {
      if (!row.original.completed_at) {
        return <span className="text-muted-foreground text-sm">-</span>;
      }
      const date = new Date(row.original.completed_at);
      return (
        <div className="flex flex-col">
          <span className="text-sm font-normal">
            {date.toLocaleString(undefined, {
              year: "numeric",
              month: "2-digit",
              day: "2-digit",
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
              hour12: false,
            })}
          </span>
        </div>
      );
    },
    enableSorting: false,
  },
  {
    id: "actions",
    header: ({ column }): React.ReactNode => (
      <DataTableColumnHeader column={column} label="Actions" />
    ),
    cell: ({ row, table }): React.ReactNode => (
      <DropdownMenu modal={false}>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Open menu"
            className="data-[state=open]:bg-muted p-0"
          >
            <Ellipsis className="h-4 w-4" aria-hidden="true" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          side="bottom"
          align="start"
          sideOffset={6}
          className="min-w-fit"
        >
          <DropdownMenuItem
            className="capitalize"
            onSelect={() => {
              const handleRowAction = table.options.meta?.handleRowAction;
              if (handleRowAction) {
                handleRowAction({ row, variant: "view" });
              }
            }}
          >
            View Details
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    ),
    enableSorting: false,
    enableHiding: false,
    size: 40,
  },
];
