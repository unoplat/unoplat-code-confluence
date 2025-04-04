import React from 'react';
import { 
  getCoreRowModel, 
  getPaginationRowModel, 
  getSortedRowModel, 
  flexRender 
} from '@tanstack/react-table';
import type { 
  ColumnDef, 
  SortingState, 
  PaginationState, 
  RowSelectionState, 
  OnChangeFn,
  Table as TableType,
  HeaderGroup,
  Header,
  Row,
  Cell
} from '@tanstack/react-table';
import type { GitHubRepoSummary } from '../types';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from './ui/table';
import { Checkbox } from './ui/checkbox';
import { Button } from './ui/button';
import { X, EyeOff } from 'lucide-react';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger,
  SelectValue
} from './ui/select';
import { Input } from './ui/input';
import { 
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger 
} from './ui/dropdown-menu';
import { DataTableColumnHeader } from './ui/data-table-column-header';
import { useDataTable } from '../hooks/use-data-table';

interface RepositoryDataTableProps {
  repositories: GitHubRepoSummary[];
  rowSelection: RowSelectionState;
  onRowSelectionChange: OnChangeFn<RowSelectionState>;
  pagination: PaginationState;
  onPaginationChange: OnChangeFn<PaginationState>;
  sorting: SortingState;
  onSortingChange: OnChangeFn<SortingState>;
  pageCount: number;
}

// Define columns outside component for better performance
const columns: ColumnDef<GitHubRepoSummary>[] = [
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
    header: ({ column }): React.ReactNode => <DataTableColumnHeader column={column} title="Repository" />,
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
    enableSorting: true,
    enableColumnFilter: true,
  },
  {
    accessorKey: 'owner_name',
    header: ({ column }): React.ReactNode => <DataTableColumnHeader column={column} title="Owner" />,
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
    enableSorting: true,
    enableColumnFilter: false,
  },
  {
    accessorKey: 'private',
    header: ({ column }): React.ReactNode => <DataTableColumnHeader column={column} title="Visibility" />,
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
  }
];

// DataTableViewOptions component
function DataTableViewOptions<TData>({
  table
}: { table: TableType<TData> }): React.ReactElement {
  // Get all columns that can be hidden
  const columns = table.getAllColumns().filter(
    (column) => column.getCanHide() && column.id !== 'select' && column.id !== 'actions'
  );

  if (!columns.length) return <></>;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="ml-auto hidden h-8 lg:flex">
          <EyeOff className="mr-2 h-4 w-4" />
          View
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[150px]">
        {columns.map((column) => {
          const meta = column.columnDef.meta;
          return (
            <DropdownMenuCheckboxItem
              key={column.id}
              className="capitalize"
              checked={column.getIsVisible()}
              onCheckedChange={(value): void => {
                column.toggleVisibility(!!value);
              }}
            >
              {meta?.label || column.id}
            </DropdownMenuCheckboxItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// DataTableToolbar component
function DataTableToolbar<TData>({
  table,
}: {
  table: TableType<TData>;
}): React.ReactElement | null {
  const isFiltered = table.getState().columnFilters.length > 0;
  
  const filterableColumns = React.useMemo(() => {
    return table.getAllColumns().filter((column) => 
      column.getCanFilter() && 
      column.id !== 'select' && 
      column.id !== 'actions'
    );
  }, [table]);

  if (!filterableColumns.length) return null;

  return (
    <div className="flex flex-col gap-2 py-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-1 flex-wrap items-center gap-2">
          {filterableColumns.length > 0 && 
            filterableColumns.map((column) => {
              const columnFilterValue = column.getFilterValue();
              const meta = column.columnDef.meta;
              if (!meta) return null;
              
              if (meta.variant === 'text') {
                return (
                  <div key={column.id} className="flex flex-1 items-center gap-2">
                    <Input
                      placeholder={meta.placeholder || `Filter ${meta.label}...`}
                      value={(columnFilterValue as string) ?? ""}
                      onChange={(event): void =>
                        column.setFilterValue(event.target.value)
                      }
                      className="h-9 w-full md:max-w-sm"
                    />
                  </div>
                );
              }
              return null;
            })
          }
          
          {isFiltered && (
            <Button
              variant="ghost"
              onClick={(): void => table.resetColumnFilters()}
              className="h-9 px-2 lg:px-3"
            >
              Reset
              <X className="ml-2 h-4 w-4" />
            </Button>
          )}
        </div>
        <div className="flex items-center gap-2">
          <DataTableViewOptions table={table} />
        </div>
      </div>
    </div>
  );
}

// DataTablePagination component
function DataTablePagination<TData>({
  table,
}: {
  table: TableType<TData>;
}): React.ReactElement {
  return (
    <div className="flex items-center justify-end space-x-2">
      <div className="flex items-center space-x-2">
        <p className="text-sm font-medium">Rows per page</p>
        <Select
          value={`${table.getState().pagination.pageSize}`}
          onValueChange={(value): void => {
            const newSize = Number(value);
            table.setPagination({
              ...table.getState().pagination,
              pageSize: newSize,
              pageIndex: 0 // Reset to first page when changing page size
            });
          }}
        >
          <SelectTrigger className="h-8 w-[90px]">
            <SelectValue placeholder={table.getState().pagination.pageSize} />
          </SelectTrigger>
          <SelectContent side="top">
            {[10, 20, 30, 40, 50].map((pageSize) => (
              <SelectItem key={pageSize} value={`${pageSize}`}>
                {pageSize}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={(): void => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
          className="h-8 w-8 p-0"
          aria-label="Go to previous page"
        >
          &lt;
        </Button>
        <div className="flex h-8 w-auto items-center justify-center text-sm">
          Page {table.getState().pagination.pageIndex + 1}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={(): void => table.nextPage()}
          disabled={!table.getCanNextPage()}
          className="h-8 w-8 p-0"
          aria-label="Go to next page"
        >
          &gt;
        </Button>
      </div>
    </div>
  );
}

export function RepositoryDataTable({
  repositories,
  rowSelection,
  onRowSelectionChange,
  pagination,
  onPaginationChange,
  sorting,
  onSortingChange,
  pageCount,
}: RepositoryDataTableProps): React.ReactElement {
  
  const { table } = useDataTable({
    data: repositories,
    columns,
    pageCount,
    initialState: {
      sorting,
      pagination,
      rowSelection,
    },
    manualPagination: true,
    manualFiltering: true,
    enableRowSelection: true,
    onRowSelectionChange,
    onSortingChange,
    onPaginationChange,
    getCoreRowModel: getCoreRowModel,
    getSortedRowModel: getSortedRowModel,
    getPaginationRowModel: getPaginationRowModel,
  });

  return (
    <div className="space-y-4">
      <DataTableToolbar table={table} />
      
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup: HeaderGroup<GitHubRepoSummary>) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header: Header<GitHubRepoSummary, unknown>) => (
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
              table.getRowModel().rows.map((row: Row<GitHubRepoSummary>) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="hover:bg-muted/50"
                >
                  {row.getVisibleCells().map((cell: Cell<GitHubRepoSummary, unknown>) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={table.getAllColumns().length}
                  className="h-24 text-center"
                >
                  No results found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredSelectedRowModel().rows.length > 0 && (
            <div>
              {table.getFilteredSelectedRowModel().rows.length} of{" "}
              {table.getFilteredRowModel().rows.length} row(s) selected
            </div>
          )}
        </div>
        <DataTablePagination table={table} />
      </div>
    </div>
  );
} 