// File: use-data-table-with-router.ts
"use client";

// Import React (for hooks) and the core functions from TanStack Table.
import {
  useReactTable,
  type TableOptions,
  type TableState,
  getCoreRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFacetedMinMaxValues,
  type PaginationState,
} from "@tanstack/react-table";
// Import useRouter and useSearch from TanStack Router.
import { useRouter } from "@tanstack/react-router";
// Import type from TanStack Table.
import type {
  ColumnDef,
  ColumnFiltersState,
  Table,
  Updater,
} from "@tanstack/react-table";
import React from "react";
import { Route as OnboardingRoute } from "../routes/_app.onboarding";
import { useDebouncedCallback } from "./use-debounced-callback";

const DEBOUNCE_MS = 300;

// Define the props that the hook accepts.
export interface UseDataTableWithRouterProps<TData>
  extends Omit<
    TableOptions<TData>,
    | "state"
    | "getCoreRowModel"
    | "manualFiltering"
    | "manualPagination"
    | "manualSorting"
  > {
  initialState?: Partial<TableState>;
  pageCount?: number; // Add pageCount prop
}

// Helper function to handle pagination changes that updates URL search params

// The custom hook that links table state with URL-managed pagination.
export function useDataTableWithRouter<TData>(
  props: UseDataTableWithRouterProps<TData>,
): { table: Table<TData> } {
  "use no memo";

  // Extract properties for table configuration.
  const { data, columns, initialState, pageCount, ...tableProps } = props;
  // Get the current router instance.
  const router = useRouter();

  const { pageIndex, perPage, filterValues } = OnboardingRoute.useSearch();

  const customPaginationState: PaginationState = React.useMemo(() => {
    return {
      pageIndex: pageIndex - 1, // zero-based index
      pageSize: perPage,
    };
  }, [pageIndex, perPage]);

  const onPaginationChange = React.useCallback(
    (updaterOrValue: Updater<PaginationState>) => {
      console.log(
        "[useDataTable] onPaginationChange called with:",
        updaterOrValue,
      );
      let newPagination: PaginationState;
      if (typeof updaterOrValue === "function") {
        newPagination = updaterOrValue(customPaginationState);
        console.log(
          "[useDataTable] New pagination (functional):",
          newPagination,
        );
      } else {
        newPagination = updaterOrValue;
        console.log("[useDataTable] New pagination (value):", newPagination);
      }

      router.navigate({
        to: OnboardingRoute.fullPath,
        search: {
          pageIndex: newPagination.pageIndex + 1,
          perPage: newPagination.pageSize,
        },
      });
    },
    [customPaginationState, pageIndex, perPage],
  );

  const filterableColumns: ColumnDef<TData>[] = React.useMemo(() => {
    const filtered = columns.filter((column) => column.enableColumnFilter);

    return filtered;
  }, [columns]);

  const debouncedSetFilterValues = useDebouncedCallback(
    (values: typeof filterValues) => {
      console.log(
        "[useDataTableWithRouter] Debounced filter value update triggered with:",
        values,
      );
      router.navigate({
        to: OnboardingRoute.fullPath,
        search: {
          pageIndex: 1,
          filterValues: values,
        },
      });
      console.log(
        "[useDataTableWithRouter] Router navigation initiated with filter values",
        values,
      );
    },
    DEBOUNCE_MS,
  );

  const initialColumnFilters: ColumnFiltersState = React.useMemo(() => {
    console.log(
      "[useDataTableWithRouter] Initializing column filters from URL search params:",
      filterValues,
    );

    const columnFilters = Object.entries(
      filterValues,
    ).reduce<ColumnFiltersState>((filters, [key, value]) => {
      if (value !== null) {
        const processedValue = Array.isArray(value)
          ? value
          : typeof value === "string" && /[^a-zA-Z0-9]/.test(value)
            ? value.split(/[^a-zA-Z0-9]+/).filter(Boolean)
            : [value];

        console.log("[useDataTableWithRouter] Processing filter:", {
          key,
          rawValue: value,
          processedValue,
        });

        filters.push({
          id: key,
          value: processedValue,
        });
      }
      return filters;
    }, []);

    console.log(
      "[useDataTableWithRouter] Initial column filters generated:",
      columnFilters,
    );
    return columnFilters;
  }, [filterValues]);

  const [columnFilters, setColumnFilters] =
    React.useState<ColumnFiltersState>(initialColumnFilters);

  const onColumnFiltersChange = React.useCallback(
    (updaterOrValue: Updater<ColumnFiltersState>) => {
      console.log(
        "[useDataTableWithRouter] onColumnFiltersChange called with:",
        typeof updaterOrValue === "function"
          ? "function updater"
          : updaterOrValue,
      );

      setColumnFilters((prev) => {
        console.log("[useDataTableWithRouter] Previous column filters:", prev);

        const next =
          typeof updaterOrValue === "function"
            ? updaterOrValue(prev)
            : updaterOrValue;

        console.log("[useDataTableWithRouter] New column filters:", next);

        const filterUpdates = next.reduce<
          Record<string, string | string[] | null>
        >((acc, filter) => {
          const column = filterableColumns.find((col) => {
            return (
              col.id === filter.id ||
              ("accessorKey" in col && col.accessorKey === filter.id)
            );
          });
          if (column) {
            // Directly assign the filter value to our update object
            acc[filter.id] = filter.value as string | string[] | null;
            console.log(
              `[useDataTableWithRouter] Adding filter for column ${filter.id}:`,
              filter.value,
            );
          } else {
            console.log(
              "[useDataTableWithRouter] Filterable columns:",
              filterableColumns,
            );
            console.log(
              `[useDataTableWithRouter] Ignoring filter for non-filterable column ${filter.id}`,
            );
          }
          return acc;
        }, {});

        // Handle filters that were removed
        for (const prevFilter of prev) {
          if (!next.some((filter) => filter.id === prevFilter.id)) {
            filterUpdates[prevFilter.id] = null;
            console.log(
              `[useDataTableWithRouter] Removing filter for column ${prevFilter.id}`,
            );
          }
        }

        if (Object.keys(filterUpdates).length === 0) {
          console.log("[useDataTableWithRouter] Filter updates is empty");
        } else {
          console.log(
            "[useDataTableWithRouter] Filter updates to be applied:",
            JSON.stringify(filterUpdates, null, 2),
          );
        }
        debouncedSetFilterValues(filterUpdates);
        return next;
      });
    },
    [debouncedSetFilterValues, filterableColumns],
  );

  const table = useReactTable({
    ...tableProps,
    data,
    columns,

    // Merge the initial state with our computed pagination.
    state: {
      ...initialState,
      pagination: customPaginationState,
      columnFilters,
    },
    enableRowSelection: true,
    onPaginationChange,
    onColumnFiltersChange,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    manualPagination: true,
    manualFiltering: true,
    manualSorting: true,
    pageCount: pageCount !== undefined ? pageCount : -1, // Use provided pageCount or default to -1 (unknown)
  });

  // Log filter state changes
  React.useEffect(() => {
    console.log("[useDataTableWithRouter] Table filter state updated:", {
      activeFilters: table.getState().columnFilters,
      filterableColumns: filterableColumns.map((c) => c.id),
      filterValues,
    });
  }, [table.getState().columnFilters, filterableColumns, filterValues]);

  console.log("[useDataTableWithRouter] Table instance created:", {
    rowCount: table.getRowModel().rows.length,
    columnCount: table.getAllColumns().length,
    pageCount: table.getPageCount(),
    currentPage: table.getState().pagination.pageIndex,
    canNextPage: table.getCanNextPage(),
    canPreviousPage: table.getCanPreviousPage(),
  });

  // Return the table instance to be used by the component.
  return { table };
}
