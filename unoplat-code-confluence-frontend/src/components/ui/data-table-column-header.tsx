import * as React from "react";
import type { Column } from "@tanstack/react-table";
import { ChevronsUpDown, EyeOff, ArrowDown, ArrowUp } from "lucide-react";
import { cn } from "../../lib/utils";
import { Button } from "./button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./dropdown-menu";

interface DataTableColumnHeaderProps<TData, TValue> {
  column: Column<TData, TValue>;
  title: string;
}

export function DataTableColumnHeader<TData, TValue>({
  column,
  title,
}: DataTableColumnHeaderProps<TData, TValue>): React.ReactElement {
  if (!column.getCanSort() && !column.getCanHide()) {
    return <div className="text-xs font-medium">{title}</div>;
  }

  return (
    <div className="flex items-center space-x-2">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="-ml-3 h-8 data-[state=open]:bg-accent"
          >
            <span>{title}</span>
            {column.getCanSort() ? (
              column.getIsSorted() === "desc" ? (
                <ArrowDown className="ml-2 h-4 w-4" />
              ) : column.getIsSorted() === "asc" ? (
                <ArrowUp className="ml-2 h-4 w-4" />
              ) : (
                <ChevronsUpDown className="ml-2 h-4 w-4" />
              )
            ) : null}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          {column.getCanSort() && (
            <>
              <DropdownMenuItem
                onClick={(): void => column.toggleSorting(false)}
                className={cn({
                  "bg-accent/50": column.getIsSorted() === "asc",
                })}
              >
                <ArrowUp className="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
                Asc
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={(): void => column.toggleSorting(true)}
                className={cn({
                  "bg-accent/50": column.getIsSorted() === "desc",
                })}
              >
                <ArrowDown className="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
                Desc
              </DropdownMenuItem>
              {column.getCanHide() && <DropdownMenuSeparator />}
            </>
          )}
          {column.getCanHide() && (
            <DropdownMenuItem onClick={(): void => column.toggleVisibility(false)}>
              <EyeOff className="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
              Hide
            </DropdownMenuItem>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
} 