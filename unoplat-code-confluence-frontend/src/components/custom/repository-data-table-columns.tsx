import React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import type { GitHubRepoSummary } from '../../types';
import { DataTableColumnHeader } from '../data-table-column-header';
import { Button } from '../ui/button';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '../ui/dropdown-menu';
import { Ellipsis } from 'lucide-react';
import { TfiGithub } from 'react-icons/tfi';
import { GrUserPolice } from 'react-icons/gr';
import { FaTripadvisor } from 'react-icons/fa';
import { HugeiconsIcon } from '@hugeicons/react';
import { TouchInteraction01Icon } from '@hugeicons/core-free-icons';

export function getRepositoryDataTableColumns({ setRowAction }: { setRowAction: React.Dispatch<React.SetStateAction<{ row: import('@tanstack/react-table').Row<GitHubRepoSummary>; variant: string } | null>> }): ColumnDef<GitHubRepoSummary>[] {
  return [
    {
      accessorKey: 'name',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Repository" icon={<TfiGithub />} />
      ),
      cell: ({ row }): React.ReactNode => (
        <div className="flex items-center">
          <a
            href={row.original.git_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline font-semibold"
          >
            {row.original.name}
          </a>
        </div>
      ),
      meta: {
        label: 'Repository',
        placeholder: 'Search repository...',
        variant: 'text',
        shortcut: 's',
      },
      enableSorting: false,
      enableColumnFilter: true,
    },
    {
      accessorKey: 'owner_name',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Owner" icon={<GrUserPolice />} />
      ),
      cell: ({ row }): React.ReactNode => (
        <a
          href={row.original.owner_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-muted-foreground hover:text-primary hover:underline text-sm"
        >
          {row.original.owner_name}
        </a>
      ),
      meta: {
        label: 'Owner',
        variant: 'text',
      },
      enableSorting: false,
      enableColumnFilter: false,
    },
    {
      accessorKey: 'private',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Visibility" icon={<FaTripadvisor />} />
      ),
      cell: ({ row }): React.ReactNode => (
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            row.original.private
              ? 'bg-destructive text-destructive-foreground'
              : 'bg-emerald-100 text-emerald-800'
          }`}
        >
          {row.original.private ? 'Private' : 'Public'}
        </span>
      ),
      enableSorting: false,
    },
    {
      id: 'actions',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Actions" icon={<HugeiconsIcon icon={TouchInteraction01Icon} />} />
      ),
      cell: ({ row }): React.ReactNode => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Open menu"
              className="p-0 data-[state=open]:bg-muted"
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
              onSelect={() => setRowAction({ row, variant: 'ingest' })}
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