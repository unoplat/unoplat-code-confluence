"use client";

import type { Column, Table } from "@tanstack/react-table";
import { X } from "lucide-react";
import * as React from "react";

import { DataTableDateFilter } from "@/components/data-table-date-filter";
import { DataTableFacetedFilter } from "@/components/data-table-faceted-filter";
import { DataTableSliderFilter } from "@/components/data-table-slider-filter";
import { DataTableViewOptions } from "@/components/data-table-view-options";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface DataTableToolbarProps<TData> extends React.ComponentProps<"div"> {
  table: Table<TData>;
}

export function DataTableToolbar<TData>({
  table,
  children,
  className,
  ...props
}: DataTableToolbarProps<TData>) {
  const isFiltered = table.getState().columnFilters.length > 0;

  const columns = React.useMemo(
    () => table.getAllColumns().filter((column) => column.getCanFilter()),
    [table],
  );

  const onReset = React.useCallback(() => {
    table.resetColumnFilters();
  }, [table]);

  // Map shortcuts to filter input IDs based on column metadata
  const shortcutMap: Record<string, string> = React.useMemo(() => {
    const map: Record<string, string> = {};
    table.getAllColumns().forEach((column) => {
      const meta: { shortcut?: string } | undefined = column.columnDef.meta as { shortcut?: string } | undefined;
      const shortcut: string | undefined = meta?.shortcut;
      if (shortcut) {
        map[shortcut.toLowerCase()] = `filter-${column.id}`;
      }
    });
    return map;
  }, [table]);

  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as Element;
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)) {
        return;
      }
      const key = event.key.toLowerCase();
      const inputId = shortcutMap[key];
      if (inputId) {
        event.preventDefault();
        const elem = document.getElementById(inputId) as HTMLInputElement | null;
        if (elem) {
          elem.focus();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [shortcutMap]);

  return (
    <div
      role="toolbar"
      aria-orientation="horizontal"
      className={cn(
        "flex w-full items-start justify-between gap-2 p-1",
        className,
      )}
      {...props}
    >
      <div className="flex flex-1 flex-wrap items-center gap-2">
        {columns.map((column) => (
          <DataTableToolbarFilter key={column.id} column={column} />
        ))}
        {isFiltered && (
          <Button
            aria-label="Reset filters"
            variant="outline"
            size="sm"
            className="border border-gray-300/60 dark:border-gray-600/60 rounded-md"
            onClick={onReset}
          >
            <X />
            Reset
          </Button>
        )}
      </div>
      <div className="flex items-center gap-2">
        {children}
        <div className="border border-gray-300/60 dark:border-gray-600/60 rounded-md p-1">
          <DataTableViewOptions table={table} />
        </div>
      </div>
    </div>
  );
}
interface DataTableToolbarFilterProps<TData> {
  column: Column<TData>;
}

function DataTableToolbarFilter<TData>({
  column,
}: DataTableToolbarFilterProps<TData>) {
  {
    const columnMeta = column.columnDef.meta;

    const onFilterRender = React.useCallback(() => {
      if (!columnMeta?.variant) return null;

      switch (columnMeta.variant) {
        case "text": {
          const shouldAutoFocus: boolean = columnMeta.label === "Repository";
          const shortcutKey: string | undefined = columnMeta.shortcut?.toUpperCase();

          return (
            <div className="group relative flex w-full max-w-[260px] items-center">
              <div className="pointer-events-none absolute left-3 flex items-center">
                <span className="text-muted-foreground">
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    viewBox="0 0 20 20" 
                    fill="currentColor" 
                    className="h-4 w-4"
                  >
                    <path 
                      fillRule="evenodd" 
                      d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" 
                      clipRule="evenodd" 
                    />
                  </svg>
                </span>
              </div>
              <Input
                id={`filter-${column.id}`}
                placeholder={columnMeta.placeholder ?? columnMeta.label}
                value={(column.getFilterValue() as string) ?? ""}
                onChange={(event) => column.setFilterValue(event.target.value)}
                className={cn(
                  "h-9 w-full border border-gray-300/60 dark:border-gray-600/60 rounded-md pl-9 pr-9",
                  "group-focus-within:border-primary group-focus-within:ring-1 group-focus-within:ring-primary",
                  shouldAutoFocus && "focus:border-primary"
                )}
                autoFocus={shouldAutoFocus}
              />
              {shortcutKey && (
                <div className="pointer-events-none absolute right-3 flex items-center text-muted-foreground">
                  <kbd
                    className="kbd kbd-xs bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 shadow-sm px-2 py-0.5 text-sm leading-none rounded"
                  >
                    {shortcutKey}
                  </kbd>
                </div>
              )}
            </div>
          );
        }

        case "number":
          return (
            <div className="relative">
              <Input
                type="number"
                inputMode="numeric"
                placeholder={columnMeta.placeholder ?? columnMeta.label}
                value={(column.getFilterValue() as string) ?? ""}
                onChange={(event) => column.setFilterValue(event.target.value)}
                className={cn("h-8 w-[120px] border border-gray-300/60 dark:border-gray-600/60 rounded-md", columnMeta.unit && "pr-8")}
              />
              {columnMeta.unit && (
                <span className="absolute top-0 right-0 bottom-0 flex items-center rounded-r-md bg-accent px-2 text-muted-foreground text-sm">
                  {columnMeta.unit}
                </span>
              )}
            </div>
          );

        case "range":
          return (
            <DataTableSliderFilter
              column={column}
              title={columnMeta.label ?? column.id}
            />
          );

        case "date":
        case "dateRange":
          return (
            <DataTableDateFilter
              column={column}
              title={columnMeta.label ?? column.id}
              multiple={columnMeta.variant === "dateRange"}
            />
          );

        case "select":
        case "multiSelect":
          return (
            <DataTableFacetedFilter
              column={column}
              title={columnMeta.label ?? column.id}
              options={columnMeta.options ?? []}
              multiple={columnMeta.variant === "multiSelect"}
            />
          );

        default:
          return null;
      }
    }, [column, columnMeta]);

    return onFilterRender();
  }
}
