import React from "react";
import type { ColumnDef } from "@tanstack/react-table";
import type { IngestedRepository } from "@/types";
import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  MoreHorizontal,
  RefreshCw,
  Trash2,
  ExternalLink,
  GitBranch,
  FileText,
} from "lucide-react";
import { StatusBadge } from "@/components/custom/StatusBadge";
import { ProviderKey } from "@/types/credential-enums";

interface ColumnOptions {
  setRowAction: React.Dispatch<
    React.SetStateAction<{
      row: import("@tanstack/react-table").Row<IngestedRepository>;
      variant: "refresh" | "delete";
    } | null>
  >;
  onGenerateAgents: (repository: IngestedRepository) => void | Promise<void>;
}

export function getIngestedRepositoriesColumns({
  setRowAction,
  onGenerateAgents,
}: ColumnOptions): ColumnDef<IngestedRepository>[] {
  return [
    {
      accessorKey: "repository_name",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} label="Repository Name" />
      ),
      cell: ({ row }) => {
        const { repository_name, repository_owner_name } = row.original;

        const githubUrl = `https://github.com/${repository_owner_name}/${repository_name}`;
        return (
          <div className="flex items-center gap-2">
            <a
              href={githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary flex items-center gap-1 text-sm font-medium hover:underline"
            >
              <span>{repository_name}</span>
              <ExternalLink className="h-3 w-3" />
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
      enableSorting: true,
      enableColumnFilter: true,
    },
    {
      accessorKey: "provider_key",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} label="Provider" />
      ),
      cell: ({ row }) => {
        const provider = row.original.provider_key;
        const providerLabel =
          provider === ProviderKey.GITHUB_OPEN
            ? "GitHub"
            : provider === ProviderKey.GITHUB_ENTERPRISE
              ? "GitHub Enterprise"
              : provider === ProviderKey.GITLAB_CE
                ? "GitLab"
                : provider === ProviderKey.GITLAB_ENTERPRISE
                  ? "GitLab Enterprise"
                  : provider.replace(/_/g, " ");
        return (
          <div className="flex items-center gap-2">
            <GitBranch className="h-4 w-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-600 capitalize">
              {providerLabel}
            </span>
          </div>
        );
      },
      meta: {
        label: "Provider",
        placeholder: "Filter by provider...",
        variant: "select",
        options: [
          { label: "GitHub", value: ProviderKey.GITHUB_OPEN },
          { label: "GitHub Enterprise", value: ProviderKey.GITHUB_ENTERPRISE },
        ],
      },
      enableSorting: true,
      enableColumnFilter: true,
      filterFn: (row, id, value) => {
        return value.includes(String(row.getValue(id)));
      },
    },
    {
      accessorKey: "repository_owner_name",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} label="Owner" />
      ),
      cell: ({ row }) => {
        return (
          <div className="flex items-center">
            <span className="text-muted-foreground text-sm">
              {row.original.repository_owner_name}
            </span>
          </div>
        );
      },
      meta: {
        label: "Owner",
        placeholder: "Filter by owner...",
        variant: "text",
      },
      enableSorting: true,
      enableColumnFilter: true,
    },
    {
      id: "actions",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} label="Actions" />
      ),
      cell: ({ row }) => {
        return (
          <DropdownMenu modal={false}>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 p-0">
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onSelect={() => {
                  void onGenerateAgents(row.original);
                }}
                className="gap-2"
              >
                <FileText className="h-4 w-4" />
                Generate Agents.md
                <StatusBadge status="alpha" className="ml-1" />
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onSelect={() => setRowAction({ row, variant: "refresh" })}
                className="gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
                <StatusBadge status="alpha" className="ml-1" />
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onSelect={() => setRowAction({ row, variant: "delete" })}
                className="text-destructive focus:text-destructive gap-2"
              >
                <Trash2 className="h-4 w-4" />
                Delete
                <StatusBadge status="beta" className="ml-1" />
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
      enableSorting: false,
      enableHiding: false,
      size: 40,
    },
  ];
}
