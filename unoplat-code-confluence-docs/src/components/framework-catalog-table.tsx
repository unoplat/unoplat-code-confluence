import { useMemo, useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table";
import type { PaginationState } from "@tanstack/react-table";
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";

import { useDataTableFilters } from "@/components/data-table-filter";
import { DataTableFilter } from "@/components/data-table-filter";
import {
  createTSTColumns,
  createTSTFilters,
} from "@/components/data-table-filter/integrations/tanstack-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  catalogColumnDefs,
  catalogFilterConfig,
} from "@/components/framework-catalog-columns";
import { Button } from "@/components/ui/button";
import type { FrameworkCatalogRow } from "@/types/framework-catalog";
import catalogData from "@/data/framework-catalog-data.json";

const typedCatalogData = catalogData as FrameworkCatalogRow[];

export function FrameworkCatalogTable() {
  const { columns, filters, actions, strategy } = useDataTableFilters({
    strategy: "client",
    data: typedCatalogData,
    columnsConfig: catalogFilterConfig,
  });

  const tstColumns = useMemo(
    () => createTSTColumns({ columns: catalogColumnDefs, configs: columns }),
    [columns],
  );

  const tstFilters = useMemo(() => createTSTFilters(filters), [filters]);

  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const table = useReactTable({
    data: typedCatalogData,
    columns: tstColumns,
    state: { columnFilters: tstFilters, pagination },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <div className="space-y-2">
      <DataTableFilter
        columns={columns}
        filters={filters}
        actions={actions}
        strategy={strategy}
      />

        <Table>
          <TableHeader className="bg-fd-muted/50">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  // For language/library columns use the configured size as a max-width
                  // so they stay compact. For the description column (size === MAX_SAFE_INTEGER)
                  // we let it stretch to fill remaining space.
                  // Ref: https://tanstack.com/table/latest/docs/guide/column-sizing
                  const isDescriptionColumn = header.column.id === "description";
                  return (
                    <TableHead
                      className="px-3 py-2 font-semibold"
                      key={header.id}
                      style={
                        isDescriptionColumn
                          ? undefined
                          : { width: header.column.getSize(), minWidth: header.column.columnDef.minSize }
                      }
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  className="border-t border-fd-border align-top"
                  key={row.id}
                >
                  {row.getVisibleCells().map((cell) => {
                    const isDescriptionCell = cell.column.id === "description";
                    return (
                      // shadcn TableCell has whitespace-nowrap by default; override it on the
                      // description column so long text wraps instead of being clipped.
                      <TableCell
                        className={
                          isDescriptionCell
                            ? "px-3 py-3 whitespace-normal"
                            : "px-3 py-3"
                        }
                        key={cell.id}
                        style={
                          isDescriptionCell
                            ? undefined
                            : { width: cell.column.getSize(), minWidth: cell.column.columnDef.minSize }
                        }
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext(),
                        )}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  className="px-3 py-6 text-center text-fd-muted-foreground"
                  colSpan={catalogColumnDefs.length}
                >
                  No frameworks match the current filters.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>

      <div className="flex items-center justify-between px-1">
        <span className="text-sm text-fd-muted-foreground">
          {table.getFilteredRowModel().rows.length} result(s)
        </span>
        <div className="flex items-center gap-2">
          <span className="text-sm text-fd-muted-foreground">
            Page {table.getState().pagination.pageIndex + 1} of{" "}
            {table.getPageCount()}
          </span>
          <Button
            variant="outline"
            size="icon-sm"
            onClick={() => table.firstPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronsLeft className="size-4" />
          </Button>
          <Button
            variant="outline"
            size="icon-sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft className="size-4" />
          </Button>
          <Button
            variant="outline"
            size="icon-sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRight className="size-4" />
          </Button>
          <Button
            variant="outline"
            size="icon-sm"
            onClick={() => table.lastPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronsRight className="size-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
