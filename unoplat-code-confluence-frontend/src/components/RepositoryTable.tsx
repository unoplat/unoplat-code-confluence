import type {
  ColumnDef,
  SortingState,
  PaginationState,
  RowSelectionState,
  OnChangeFn,
} from '@tanstack/react-table';
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table';
import type { GitHubRepoSummary } from '../types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Checkbox } from './ui/checkbox';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { FaGithubAlt } from "react-icons/fa";
import React from 'react';

interface GitHubRepositoryTableProps {
  repositories: GitHubRepoSummary[];
  rowSelection: RowSelectionState;
  onRowSelectionChange: OnChangeFn<RowSelectionState>;
  globalFilter: string;
  onGlobalFilterChange: (value: string) => void;
  pagination: PaginationState;
  onPaginationChange: OnChangeFn<PaginationState>;
  sorting: SortingState;
  onSortingChange: OnChangeFn<SortingState>;
  searchInputRef: React.RefObject<HTMLInputElement | null>;
}

// Define columns outside component for better performance
const columns: ColumnDef<GitHubRepoSummary>[] = [
  {
    id: 'select',
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value): void => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value): void => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'name',
    header: 'Repository Name',
    cell: ({ row }) => (
      <div className="font-medium">
        {row.original.name}
      </div>
    ),
  },
  {
    accessorKey: 'owner_name',
    header: 'Owner',
    cell: ({ row }) => (
      <a 
        href={row.original.owner_url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-primary hover:underline"
      >
        {row.original.owner_name}
      </a>
    ),
  },
  {
    accessorKey: 'private',
    header: 'Visibility',
    cell: ({ row }) => (
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
  },
  {
    id: 'github_link',
    header: () => (
      <div className="text-center w-full">GitHub Link</div>
    ),
    cell: ({ row }) => (
      <div className="flex justify-center w-full">
        <a
          href={row.original.git_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:text-primary/80"
          aria-label="View on GitHub"
          title="View on GitHub"
        >
          <FaGithubAlt className="w-5 h-5" />
        </a>
      </div>
    ),
  },
];

export function RepositoryTable({
  repositories,
  rowSelection,
  onRowSelectionChange,
  globalFilter,
  onGlobalFilterChange,
  pagination,
  onPaginationChange,
  sorting,
  onSortingChange,
  searchInputRef,
}: GitHubRepositoryTableProps): React.ReactElement {
  
  const table = useReactTable({
    data: repositories,
    columns,
    state: {
      sorting,
      globalFilter,
      pagination,
      rowSelection,
    },
    enableRowSelection: true,
    onRowSelectionChange,
    onSortingChange,
    onGlobalFilterChange,
    onPaginationChange,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <>
      {/* Search Input */}
      <div className="flex items-center mb-4">
        <Input
          ref={searchInputRef}
          type="text"
          placeholder="Search for repositories…"
          value={globalFilter ?? ""}
          onChange={(e): void => onGlobalFilterChange(e.target.value)}
          className="max-w-sm"
        />
        <div className="ml-auto text-sm text-muted-foreground">
          {Object.keys(rowSelection).length} of{" "}
          {repositories.length} row(s) selected
        </div>
      </div>

      {/* Repository Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No repositories found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <div className="flex-1 text-sm text-muted-foreground">
          Showing page {table.getState().pagination.pageIndex + 1} of{" "}
          {table.getPageCount()}
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={(): void => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={(): void => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </>
  );
} 