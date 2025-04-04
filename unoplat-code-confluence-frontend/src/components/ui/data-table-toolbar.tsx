import * as React from "react";
import type { Table } from "@tanstack/react-table";
import { X } from "lucide-react";
import { Button } from "./button";
import { Input } from "./input";
import { DataTableViewOptions } from "./data-table-view-options";

interface DataTableToolbarProps<TData> {
  table: Table<TData>;
  children?: React.ReactNode;
}

export function DataTableToolbar<TData>({
  table,
  children,
}: DataTableToolbarProps<TData>): React.ReactElement | null {
  const isFiltered = table.getState().columnFilters.length > 0;
  
  const filterableColumns = React.useMemo(() => {
    return table.getAllColumns().filter((column) => 
      column.getCanFilter() && 
      column.id !== 'select' && 
      column.id !== 'actions'
    );
  }, [table]);

  if (!filterableColumns.length && !children) return null;

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
          {children}
          <DataTableViewOptions table={table} />
        </div>
      </div>
    </div>
  );
} 