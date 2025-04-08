import type { Table } from "@tanstack/react-table";
import {
  ChevronLeft,
  ChevronRight,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  ChevronsLeft,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  ChevronsRight,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

interface DataTablePaginationProps<TData> extends React.ComponentProps<"div"> {
  table: Table<TData>;
  pageSizeOptions?: number[];
  showRowsPerPage?: boolean;
}

export function DataTablePagination<TData>({
  table,
  pageSizeOptions = [10, 20, 30, 40, 50],
  showRowsPerPage = false,
  className,
  ...props
}: DataTablePaginationProps<TData>) {
  console.log('[DataTablePagination] Rendering with table state:', {
    pageIndex: table.getState().pagination.pageIndex,
    pageSize: table.getState().pagination.pageSize,
    canNextPage: table.getCanNextPage(),
    canPreviousPage: table.getCanPreviousPage(),
    pageCount: table.getPageCount()
  });
  
  console.log('DataTablePagination props:', { showRowsPerPage });
  console.log('Rows per page section should be:', showRowsPerPage ? 'visible' : 'hidden');
  
  const handlePreviousPage = () => {
    console.log('[DataTablePagination] Previous page button clicked');
    console.log('[DataTablePagination] Before change:', {
      pageIndex: table.getState().pagination.pageIndex,
      canPreviousPage: table.getCanPreviousPage()
    });
    table.previousPage();
    console.log('[DataTablePagination] After change:', {
      pageIndex: table.getState().pagination.pageIndex
    });
  };

  const handleNextPage = () => {
    console.log('[DataTablePagination] Next page button clicked');
    console.log('[DataTablePagination] Before change:', {
      pageIndex: table.getState().pagination.pageIndex,
      canNextPage: table.getCanNextPage()
    });
    table.nextPage();
    console.log('[DataTablePagination] After change:', {
      pageIndex: table.getState().pagination.pageIndex
    });
  };

  const handleFirstPage = () => {
    console.log('[DataTablePagination] First page button clicked');
    table.setPageIndex(0);
  };

  const handleLastPage = () => {
    console.log('[DataTablePagination] Last page button clicked');
    table.setPageIndex(table.getPageCount() - 1);
  };

  const handlePageSizeChange = (value: string) => {
    console.log('[DataTablePagination] Page size change:', value);
    table.setPageSize(Number(value));
  };
  
  return (
    <div
      className={cn(
        "flex w-full flex-col-reverse items-center justify-between gap-4 overflow-auto p-1 sm:flex-row sm:gap-8",
        className,
      )}
      {...props}
    >
      <div className="flex-1 whitespace-nowrap text-muted-foreground text-sm">
        {table.getFilteredSelectedRowModel().rows.length} of{" "}
        {table.getFilteredRowModel().rows.length} row(s) selected.
      </div>
      <div className="flex flex-col-reverse items-center gap-4 sm:flex-row sm:gap-6 lg:gap-8">
        {showRowsPerPage && (
          <div className="flex items-center space-x-2">
            <p className="whitespace-nowrap font-medium text-sm">Rows per page</p>
            <Select
              value={`${table.getState().pagination.pageSize}`}
              onValueChange={handlePageSizeChange}
            >
              <SelectTrigger className="h-8 w-[4.5rem] [&[data-size]]:h-8">
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
        )}
        <div className="flex items-center justify-center font-medium text-sm">
          Page {table.getState().pagination.pageIndex + 1} 
          {/* {table.getPageCount()} */}
        </div>
        <div className="flex items-center space-x-2">
          <Button
            aria-label="Go to first page"
            variant="outline"
            size="icon"
            className="size-8"
            onClick={handleFirstPage}
            disabled={true}
          >
            <ChevronsLeft />
          </Button>
          <Button
            aria-label="Go to previous page"
            variant="outline"
            size="icon"
            onClick={handlePreviousPage}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft />
          </Button>
          <Button
            aria-label="Go to next page"
            variant="outline"
            size="icon"
            onClick={handleNextPage}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRight />
          </Button>
          <Button
            aria-label="Go to last page"
            variant="outline"
            size="icon"
            className="size-8"
            onClick={handleLastPage}
            disabled={true}
          >
            <ChevronsRight />
          </Button>
        </div>
      </div>
    </div>
  );
}
