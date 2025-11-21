import React from "react";
import type { ColumnDef } from "@tanstack/react-table";
import type { GitHubRepoSummary } from "../../types";
import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "../ui/dropdown-menu";
import { Ellipsis } from "lucide-react";

export function getRepositoryDataTableColumns({
  onIngest,
}: {
  onIngest: (repo: GitHubRepoSummary) => void;
}): ColumnDef<GitHubRepoSummary>[] {
  return [
    {
      id: "name",
      accessorKey: "name",
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} label="Repository" />
      ),
      cell: ({ row }): React.ReactNode => (
        <div className="flex items-center">
          <a
            href={row.original.git_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary text-sm font-normal hover:underline"
          >
            {row.original.name}
          </a>
        </div>
      ),
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
      id: "owner_name",
      accessorKey: "owner_name",
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} label="Owner" />
      ),
      cell: ({ row }): React.ReactNode => (
        <a
          href={row.original.owner_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-muted-foreground hover:text-primary text-sm font-normal hover:underline"
        >
          {row.original.owner_name}
        </a>
      ),
      meta: {
        label: "Owner",
        variant: "text",
      },
      enableSorting: false,
      enableColumnFilter: false,
    },
    {
      id: "private",
      accessorKey: "private",
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} label="Visibility" />
      ),
      cell: ({ row }): React.ReactNode => (
        <Badge variant={row.original.private ? "default" : "secondary"}>
          {row.original.private ? "Private" : "Public"}
        </Badge>
      ),
      enableSorting: false,
    },
    {
      id: "actions",
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} label="Actions" />
      ),
      cell: ({ row }): React.ReactNode => (
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
              onSelect={() => onIngest(row.original)}
            >
              Ingest Repo
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
      enableSorting: false,
      enableHiding: false,
      size: 40,
    },
  ];
}
