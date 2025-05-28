import { type Table as TanstackTable, flexRender } from "@tanstack/react-table";
import type * as React from "react";
import { useEffect } from "react";

import { DataTablePagination } from "@/components/data-table-pagination";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getCommonPinningStyles } from "@/lib/data-table";
import { cn } from "@/lib/utils";

interface DataTableProps<TData> extends React.ComponentProps<"div"> {
  table: TanstackTable<TData>;
  actionBar?: React.ReactNode;
  showRowsPerPage?: boolean;
  isLoading?: boolean;
}

export function DataTable<TData>({
  table,
  actionBar,
  showRowsPerPage = false,
  isLoading = false,
  children,
  className,
  ...props
}: DataTableProps<TData>): React.ReactElement {
  console.log('[DataTable] Rendering with table state:', {
    pageIndex: table.getState().pagination.pageIndex,
    pageSize: table.getState().pagination.pageSize,
    rowCount: table.getRowModel().rows.length,
    canNextPage: table.getCanNextPage(),
    canPreviousPage: table.getCanPreviousPage(),
    isLoading
  });
  
  console.log('DataTable props:', { showRowsPerPage, isLoading });
  
  // Log table state changes to track pagination updates
  useEffect(() => {
    console.log('[DataTable] Table pagination state changed:', {
      pageIndex: table.getState().pagination.pageIndex,
      pageSize: table.getState().pagination.pageSize,
      canNextPage: table.getCanNextPage(),
      canPreviousPage: table.getCanPreviousPage()
    });
  }, [table.getState().pagination]);
  
  return (
    <div
      className={cn("flex w-full flex-col gap-2.5 overflow-auto", className)}
      {...props}
    >
      {children}
      <div className="overflow-auto rounded-md border border-border bg-card">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    colSpan={header.colSpan}
                    style={{
                      ...getCommonPinningStyles({ column: header.column }),
                    }}
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              // Only skeletonize the rows, not the whole table
              Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i} className="hover:bg-transparent">
                  {table.getAllColumns().map((_column, j) => (
                    <TableCell key={j}>
                      <div className="h-6 w-full animate-pulse bg-muted rounded" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell
                      key={cell.id}
                      style={{
                        ...getCommonPinningStyles({ column: cell.column }),
                      }}
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
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
                  {"No results."}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex flex-col gap-2.5">
        {/* To enable - showRowsPerPage={showRowsPerPage} */}
        <DataTablePagination table={table}  />
        {actionBar &&
          table.getFilteredSelectedRowModel().rows.length > 0 &&
          actionBar}
      </div>
    </div>
  );
}
