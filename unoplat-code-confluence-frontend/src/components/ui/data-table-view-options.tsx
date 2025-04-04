import * as React from "react";
import type { Table } from "@tanstack/react-table";
import { DropdownMenu, DropdownMenuCheckboxItem, DropdownMenuContent, DropdownMenuTrigger } from "./dropdown-menu";
import { Button } from "./button";
import { EyeOff } from "lucide-react";

interface DataTableViewOptionsProps<TData> {
  table: Table<TData>;
}

export function DataTableViewOptions<TData>({
  table,
}: DataTableViewOptionsProps<TData>): React.ReactElement {
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