import * as React from "react";
import type { Table } from "@tanstack/react-table";
import { Button } from "./button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./select";

interface DataTablePaginationProps<TData> {
  table: Table<TData>;
  pageSizeOptions?: number[];
}

export function DataTablePagination<TData>({
  table,
  pageSizeOptions = [10, 20, 30, 40, 50],
}: DataTablePaginationProps<TData>): React.ReactElement {
  return (
    <div className="flex items-center justify-end space-x-2">
      <div className="flex items-center space-x-2">
        <p className="text-sm font-medium">Rows per page</p>
        <Select
          value={`${table.getState().pagination.pageSize}`}
          onValueChange={(value): void => {
            table.setPageSize(Number(value));
          }}
        >
          <SelectTrigger className="h-8 w-[70px]">
            <SelectValue placeholder={table.getState().pagination.pageSize} />
          </SelectTrigger>
          <SelectContent side="top">
            {pageSizeOptions.map((pageSize) => (
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
          Page {table.getState().pagination.pageIndex + 1} of{" "}
          {table.getPageCount() > 0 ? table.getPageCount() : 1}
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