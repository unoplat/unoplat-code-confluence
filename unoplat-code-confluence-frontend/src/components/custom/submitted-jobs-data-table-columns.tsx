import React from "react";
import type { ColumnDef } from "@tanstack/react-table";
import type { ParentWorkflowJobResponse, JobStatus } from "../../types";
import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "../ui/dropdown-menu";
import {
  Ellipsis,
  AlertCircle,
  CheckCircle,
  Clock,
  PauseCircle,
  RefreshCw,
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
    default:
      return <Clock className="text-muted-foreground h-4 w-4" />;
  }
};

export const getStatusVariant = (
  status: JobStatus,
): "completed" | "failed" | "pending" | "running" | "cancelled" => {
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
    default:
      return "cancelled";
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
