import React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import type { GitHubRepoSummary } from '../../types';
import { DataTableColumnHeader } from '../data-table-column-header';
import { Checkbox } from '../ui/checkbox';

export function getRepositoryDataTableColumns(): ColumnDef<GitHubRepoSummary>[] {
  return [
    {
      id: 'select',
      header: (): React.ReactNode => null,
      cell: ({ row }): React.ReactNode => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value: boolean): void => row.toggleSelected(!!value)}
          aria-label="Select row"
        />
      ),
      enableSorting: false,
      enableHiding: false,
    },
    {
      accessorKey: 'name',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Repository" />
      ),
      cell: ({ row }): React.ReactNode => (
        <div className="flex items-center">
          <a
            href={row.original.git_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            {row.original.name}
          </a>
        </div>
      ),
      meta: {
        label: 'Repository',
        placeholder: 'Search repository...',
        variant: 'text',
      },
      enableSorting: false,
      enableColumnFilter: true,
    },
    {
      accessorKey: 'owner_name',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Owner" />
      ),
      cell: ({ row }): React.ReactNode => (
        <a
          href={row.original.owner_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:underline"
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
        <DataTableColumnHeader column={column} title="Visibility" />
      ),
      cell: ({ row }): React.ReactNode => (
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            row.original.private
              ? 'bg-destructive/10 text-destructive'
              : 'bg-primary/10 text-primary'
          }`}
        >
          {row.original.private ? 'Private' : 'Public'}
        </span>
      ),
      meta: {
        label: 'Visibility',
        variant: 'select',
        options: [
          { label: 'Public', value: 'false' },
          { label: 'Private', value: 'true' },
        ],
      },
      enableSorting: false,
    },
  ];
} 