import React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import type { IngestedRepository } from '../../types';
import { DataTableColumnHeader } from '@/components/data-table-column-header';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal, RefreshCw, Trash2, ExternalLink } from 'lucide-react';

interface ColumnOptions {
  setRowAction: React.Dispatch<React.SetStateAction<{
    row: import('@tanstack/react-table').Row<IngestedRepository>;
    variant: 'refresh' | 'delete';
  } | null>>;
}

export function getIngestedRepositoriesColumns({ setRowAction }: ColumnOptions): ColumnDef<IngestedRepository>[] {
  return [
    {
      accessorKey: 'repository_name',
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Repository Name" />
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
              className="flex items-center gap-1 text-sm font-medium text-primary hover:underline"
            >
              <span>{repository_name}</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        );
      },
      meta: {
        label: 'Repository',
        placeholder: 'Search repository...',
        variant: 'text',
        shortcut: 's',
      },
      enableSorting: true,
      enableColumnFilter: true,
    },
    {
      accessorKey: 'repository_owner_name',
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Owner" />
      ),
      cell: ({ row }) => {
        return (
          <div className="flex items-center">
            <span className="text-sm text-muted-foreground">
              {row.original.repository_owner_name}
            </span>
          </div>
        );
      },
      meta: {
        label: 'Owner',
        placeholder: 'Filter by owner...',
        variant: 'text',
      },
      enableSorting: true,
      enableColumnFilter: true,
    },
    {
      id: 'actions',
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Actions" />
      ),
      cell: ({ row }) => {
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 p-0"
              >
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onSelect={() => setRowAction({ row, variant: 'refresh' })}
                className="gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh (Alpha)
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onSelect={() => setRowAction({ row, variant: 'delete' })}
                className="gap-2 text-destructive focus:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
                Delete (Beta)
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